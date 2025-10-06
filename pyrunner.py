#!/usr/bin/env python3
import argparse,json,logging,os,subprocess,sys,time,venv,hashlib,threading,shutil,concurrent.futures
from pathlib import Path
from typing import Dict,List,Optional,Tuple,Set
import yaml,shlex,itertools
from dataclasses import dataclass,asdict
from datetime import datetime,timedelta
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
class _Spinner:
    def __init__(self,msg:str):
        self.msg=msg
        self.frames='⠋⠙⠸⠴⠦⠇'
        self._stop=threading.Event()
        self._thr=None
    def _run(self):
        cycle=itertools.cycle(self.frames)
        while not self._stop.is_set():
            f=next(cycle)
            sys.stdout.write(f"\r{self.msg} {f}")
            sys.stdout.flush()
            time.sleep(0.08)
        sys.stdout.write("\r"+(" "*(len(self.msg)+2))+"\r")
        sys.stdout.flush()
    def start(self):
        if self._thr and self._thr.is_alive():return
        self._stop.clear()
        self._thr=threading.Thread(target=self._run,daemon=True)
        self._thr.start()
    def stop(self):
        self._stop.set()
        if self._thr:self._thr.join()
def _spin_call(msg:str,fn,*args,**kwargs):
    s=_Spinner(msg);s.start()
    try:return fn(*args,**kwargs)
    finally:s.stop()
def _spin_sleep(msg:str,seconds:float=2.5):
    s=_Spinner(msg);s.start()
    try:time.sleep(seconds)
    finally:s.stop()
def _is_first_run()->bool:
    return len(sys.argv)==1
class PyRunnerError(Exception):pass
@dataclass
class EnvironmentInfo:
    name:str;path:str;created_at:float;last_used:float;scripts:List[str];size_mb:float;python_version:str;dependency_count:int
@dataclass
class LockEntry:
    name:str;version:str;hash:str;dependencies:List[str]
class FileWatcher(FileSystemEventHandler):
    def __init__(self,runner,script_path,env_path,extra_args,env_vars,config_path):
        self.runner=runner;self.script_path=script_path;self.env_path=env_path;self.extra_args=extra_args;self.env_vars=env_vars;self.config_path=config_path;self.process=None;self.restart_needed=False;self.deps_changed=False
    def on_modified(self,event):
        if event.is_directory:return
        file_path=Path(event.src_path)
        if file_path.suffix=='.py' and file_path.samefile(Path(self.script_path)):
            print(f"\n🔄 Script changed: {file_path.name}");self.restart_needed=True;self._restart_script()
        elif file_path.name in ['requirements.txt','config.yaml','config.yml'] and file_path.samefile(Path(self.config_path)):
            print(f"\n📦 Dependencies changed: {file_path.name}");self.deps_changed=True;self._update_and_restart()
    def _restart_script(self):
        if self.process and self.process.poll() is None:
            print("⏹️  Stopping current process...");self.process.terminate();self.process.wait()
        print("🚀 Restarting script...")
        try:
            python_path=self.runner.get_python_path(self.env_path);cmd=[str(python_path),str(self.script_path)]
            if self.extra_args:cmd.extend(self.extra_args)
            env=os.environ.copy()
            if self.env_vars:env.update(self.env_vars)
            self.process=subprocess.Popen(cmd,env=env);print(f"✅ Script restarted (PID: {self.process.pid})")
        except Exception as e:print(f"❌ Failed to restart: {e}")
    def _update_and_restart(self):
        if self.process and self.process.poll() is None:
            print("⏹️  Stopping current process...");self.process.terminate();self.process.wait()
        print("📦 Updating dependencies...")
        try:
            config=self.runner.parse_config(self.config_path);self.runner.install_dependencies(self.env_path,config,force_update=True);print("✅ Dependencies updated");self._restart_script()
        except Exception as e:print(f"❌ Failed to update dependencies: {e}")
class PyRunner:
    def __init__(self):
        self.logger=None;self.log_file=None;self.cache_dir=Path.home()/'.pyrunner_cache';self.cache_dir.mkdir(exist_ok=True)
    def setup_logging(self,log_location:Optional[str]=None,log_name:Optional[str]=None,script_name:str="script")->None:
        if not log_location:return
        log_dir=Path(log_location);log_dir.mkdir(parents=True,exist_ok=True)
        if not log_name:log_name=f"Run_Logs_For_{script_name}.log"
        self.log_file=log_dir/log_name
        logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(message)s',handlers=[logging.FileHandler(self.log_file),logging.StreamHandler(sys.stdout)])
        self.logger=logging.getLogger(__name__);self.logger.info(f"PyRunner started - Log file: {self.log_file}")
    def enhanced_error_message(self,error:Exception,context:str="")->str:
        error_msg=str(error);suggestions=[]
        if "pip" in error_msg.lower() and "install" in error_msg.lower():
            if "permission denied" in error_msg.lower():suggestions+=["Try running without sudo (virtual environments don't need it)","Check if the environment directory has correct permissions"]
            elif "could not find" in error_msg.lower():suggestions+=["Check if the package name is spelled correctly","Try: pip search <package_name> to find the correct name"]
            elif "version" in error_msg.lower() and "conflict" in error_msg.lower():suggestions+=["There's a dependency version conflict","Try: pyrunner --fix-env <env_name> to resolve conflicts","Or use: --force-update to override version constraints"]
        elif "script file not found" in error_msg.lower():suggestions+=[f"Check if the file exists: ls -la {context}","Make sure you're in the correct directory","Use absolute path if the script is in another directory"]
        elif "python executable not found" in error_msg.lower():suggestions+=["The virtual environment seems corrupted",f"Try: pyrunner --fix-env {context}",f"Or reset: pyrunner --reset {context}"]
        enhanced_msg=f"❌ Error: {error_msg}"
        if context:enhanced_msg+=f"\n📍 Context: {context}"
        if suggestions:
            enhanced_msg+="\n💡 Suggestions:"
            for s in suggestions:enhanced_msg+=f"\n   • {s}"
        return enhanced_msg
    def smart_auto_detect_config(self,script_path:str)->Optional[str]:
        script_dir=Path(script_path).parent;config_files=[script_dir/"config.yaml",script_dir/"config.yml",script_dir/"requirements.txt",script_dir/"pyproject.toml"]
        for c in config_files:
            if c.exists():return str(c)
        return None
    def create_quick_config(self,script_path:str,packages:List[str])->str:
        script_dir=Path(script_path).parent;config_path=script_dir/"requirements.txt"
        with open(config_path,'w')as f:
            for p in packages:f.write(f"{p}\n")
        print(f"✅ Created {config_path} with {len(packages)} packages");return str(config_path)
    def add_package_to_env(self,env_path:Path,package:str)->None:
        pip_path=self.get_pip_path(env_path)
        if not pip_path.exists():raise PyRunnerError(f"Environment not found or invalid: {env_path}")
        try:
            print(f"📦 Installing {package}...");subprocess.run([str(pip_path),"install",package],capture_output=True,text=True,check=True);print(f"✅ Successfully installed {package}")
            config_file=env_path/'.pyrunner'/'config.json'
            if config_file.exists():
                with open(config_file,'r')as f:metadata=json.load(f)
                metadata['last_updated']=time.time()
                with open(config_file,'w')as f:json.dump(metadata,f,indent=2)
        except subprocess.CalledProcessError as e:raise PyRunnerError(self.enhanced_error_message(e,f"installing {package}"))
    def remove_package_from_env(self,env_path:Path,package:str)->None:
        pip_path=self.get_pip_path(env_path)
        if not pip_path.exists():raise PyRunnerError(f"Environment not found or invalid: {env_path}")
        try:
            print(f"🗑️  Removing {package}...");subprocess.run([str(pip_path),"uninstall",package,"-y"],capture_output=True,text=True,check=True);print(f"✅ Successfully removed {package}")
        except subprocess.CalledProcessError as e:raise PyRunnerError(self.enhanced_error_message(e,f"removing {package}"))
    def launch_shell(self,env_path:Path)->None:
        if not env_path.exists():raise PyRunnerError(f"Environment not found: {env_path}")
        python_path=self.get_python_path(env_path)
        if not python_path.exists():raise PyRunnerError(f"Python executable not found: {python_path}")
        print(f"🐚 Launching shell in environment: {env_path.name}");print("💡 Type 'exit' to return to normal shell")
        if sys.platform=="win32":activate_script=env_path/"Scripts"/"activate.bat";os.system(f'cmd /k "{activate_script}"')
        else:activate_script=env_path/"bin"/"activate";shell=os.environ.get('SHELL','/bin/bash');os.system(f'{shell} --rcfile <(echo "source {activate_script}")')
    def doctor_diagnose(self,env_path:Path=None)->Dict[str,List[str]]:
        issues={"critical":[],"warnings":[],"suggestions":[]}
        envs_to_check=[env_path]if env_path else[env.path for env in self.list_environments()]
        for e in envs_to_check:
            env_path=Path(e);n=env_path.name
            if not env_path.exists():issues["critical"].append(f"{n}: Environment directory missing");continue
            python_path=self.get_python_path(env_path);pip_path=self.get_pip_path(env_path)
            if not python_path.exists():issues["critical"].append(f"{n}: Python executable missing")
            if not pip_path.exists():issues["critical"].append(f"{n}: Pip executable missing")
            try:
                r=subprocess.run([str(pip_path),"check"],capture_output=True,text=True,timeout=30)
                if r.returncode!=0 and r.stdout:issues["warnings"].append(f"{n}: Dependency conflicts detected")
            except:issues["warnings"].append(f"{n}: Could not check dependencies")
            env_info=self.get_environment_info(env_path)
            if env_info:
                if env_info.size_mb>500:issues["suggestions"].append(f"{n}: Large environment ({env_info.size_mb:.1f}MB) - consider cleanup")
                d=(time.time()-env_info.last_used)/(24*60*60)
                if d>30:issues["suggestions"].append(f"{n}: Unused for {d:.0f} days - consider removal")
        return issues
    def auto_fix_environment(self,env_path:Path)->bool:
        print(f"🔧 Auto-fixing environment: {env_path.name}")
        try:
            is_valid,validation_issues=self.validate_environment(env_path)
            if "Python executable missing" in str(validation_issues):
                print("🔨 Recreating corrupted environment...");shutil.rmtree(env_path);self.create_virtual_environment(env_path);print("✅ Environment recreated");return True
            pip_path=self.get_pip_path(env_path)
            if pip_path.exists():
                print("🔍 Checking for dependency conflicts...")
                try:
                    r=subprocess.run([str(pip_path),"check"],capture_output=True,text=True)
                    if r.returncode!=0:
                        print("🔨 Fixing dependency conflicts...");subprocess.run([str(pip_path),"install","--upgrade","--force-reinstall","pip"],check=True,capture_output=True);print("✅ Dependencies fixed")
                except:print("⚠️  Could not auto-fix dependency conflicts")
            print("🧹 Cleaning pip cache...")
            try:subprocess.run([str(pip_path),"cache","purge"],capture_output=True,text=True);print("✅ Cache cleaned")
            except:pass
            return True
        except Exception as e:
            print(f"❌ Auto-fix failed: {e}");return False
    def create_environment_template(self,template_name:str,template_path:Path)->None:
        templates_dir=self.cache_dir/'templates';templates_dir.mkdir(exist_ok=True)
        template_config={'name':template_name,'created_at':time.time(),'base_dependencies':[],'python_version':None,'description':f"Template environment: {template_name}"}
        template_file=templates_dir/f"{template_name}.json"
        with open(template_file,'w')as f:json.dump(template_config,f,indent=2)
        if self.logger:self.logger.info(f"Environment template created: {template_name}")
    def clone_environment(self,source_env:Path,target_env:Path)->None:
        if not source_env.exists():raise PyRunnerError(f"Source environment not found: {source_env}")
        if target_env.exists():raise PyRunnerError(f"Target environment already exists: {target_env}")
        try:
            if self.logger:self.logger.info(f"Cloning environment from {source_env} to {target_env}")
            shutil.copytree(source_env,target_env);metadata_file=target_env/'.pyrunner'/'config.json'
            if metadata_file.exists():
                with open(metadata_file,'r')as f:metadata=json.load(f)
                metadata['cloned_from']=str(source_env);metadata['cloned_at']=time.time()
                with open(metadata_file,'w')as f:json.dump(metadata,f,indent=2)
            if self.logger:self.logger.info("Environment cloned successfully")
        except Exception as e:raise PyRunnerError(f"Failed to clone environment: {e}")
    def parse_config(self,config_path:str)->Dict:
        config_file=Path(config_path)
        if not config_file.exists():raise PyRunnerError(f"Configuration file not found: {config_path}")
        if config_file.suffix.lower() in ['.yaml','.yml']:return self._parse_yaml_config(config_file)
        elif config_file.suffix.lower()=='.txt' or config_file.name=='requirements.txt':return self._parse_requirements_txt(config_file)
        else:raise PyRunnerError(f"Unsupported configuration file format: {config_file.suffix}")
    def _parse_yaml_config(self,config_file:Path)->Dict:
        try:
            with open(config_file,'r')as f:config=yaml.safe_load(f)
            profiles=config.get('profiles',{});current_profile=config.get('active_profile','default')
            if current_profile in profiles:
                profile_config=profiles[current_profile];base_deps=config.get('dependencies',[]);profile_deps=profile_config.get('dependencies',[]);all_deps=base_deps+profile_deps
                profile_env_vars=profile_config.get('env_vars',{});base_env_vars=config.get('environment_variables',{});all_env_vars={**base_env_vars,**profile_env_vars}
            else:all_deps=config.get('dependencies',[]);all_env_vars=config.get('environment_variables',{})
            result={'python_version':config.get('python_version'),'requirements_file':config.get('requirements_file'),'dependencies':all_deps,'dev_dependencies':config.get('dev_dependencies',[]),'environment_variables':all_env_vars,'config_type':'yaml','profiles':profiles,'active_profile':current_profile,'hot_reload':config.get('hot_reload',False),'template':config.get('template')}
            if self.logger:self.logger.info(f"Parsed YAML config: {config_file} (profile: {current_profile})")
            return result
        except yaml.YAMLError as e:raise PyRunnerError(f"Error parsing YAML config: {e}")
    def _parse_requirements_txt(self,config_file:Path)->Dict:
        try:
            with open(config_file,'r')as f:dependencies=[line.strip() for line in f if line.strip() and not line.startswith('#')]
            result={'python_version':None,'requirements_file':str(config_file),'dependencies':dependencies,'dev_dependencies':[],'environment_variables':{},'config_type':'requirements','profiles':{},'active_profile':'default','hot_reload':False,'template':None}
            if self.logger:self.logger.info(f"Parsed requirements.txt: {config_file} ({len(dependencies)} packages)")
            return result
        except Exception as e:raise PyRunnerError(f"Error parsing requirements.txt: {e}")
    def generate_lock_file(self,env_path:Path,config:Dict)->None:
        pip_path=self.get_pip_path(env_path)
        if not pip_path.exists():return
        try:
            r=subprocess.run([str(pip_path),"freeze"],capture_output=True,text=True,check=True)
            lock_entries=[]
            for line in r.stdout.strip().split('\n'):
                if line and '==' in line:
                    name,version=line.split('==',1);lock_entries.append(LockEntry(name=name.strip(),version=version.strip(),hash="",dependencies=[]))
            lock_file=env_path/'.pyrunner'/'requirements.lock';lock_data={'generated_at':time.time(),'python_version':config.get('python_version'),'entries':[asdict(e) for e in lock_entries]}
            with open(lock_file,'w')as f:json.dump(lock_data,f,indent=2)
            if self.logger:self.logger.info(f"Lock file generated with {len(lock_entries)} packages")
        except subprocess.CalledProcessError as e:
            if self.logger:self.logger.warning(f"Failed to generate lock file: {e}")
    def install_from_lock_file(self,env_path:Path)->bool:
        lock_file=env_path/'.pyrunner'/'requirements.lock'
        if not lock_file.exists():return False
        pip_path=self.get_pip_path(env_path)
        if not pip_path.exists():return False
        try:
            with open(lock_file,'r')as f:lock_data=json.load(f)
            if self.logger:self.logger.info("Installing from lock file...")
            packages=[f"{e['name']}=={e['version']}" for e in lock_data['entries']]
            if packages:
                r=subprocess.run([str(pip_path),"install"]+packages,capture_output=True,text=True)
                if r.returncode==0:
                    if self.logger:self.logger.info(f"Installed {len(packages)} packages from lock file")
                    return True
                else:
                    if self.logger:self.logger.warning(f"Lock file installation failed: {r.stderr}")
                    return False
            return True
        except Exception as e:
            if self.logger:self.logger.warning(f"Failed to install from lock file: {e}")
            return False
    def _get_config_hash(self,config:Dict)->str:
        config_for_hash={'dependencies':sorted(config['dependencies']),'dev_dependencies':sorted(config['dev_dependencies']),'python_version':config['python_version'],'active_profile':config.get('active_profile','default')}
        if config['requirements_file'] and config['config_type']=='yaml':
            req_file=Path(config['requirements_file'])
            if req_file.exists():
                with open(req_file,'r')as f:config_for_hash['requirements_content']=f.read()
        config_str=json.dumps(config_for_hash,sort_keys=True);return hashlib.md5(config_str.encode()).hexdigest()
    def _get_stored_config_hash(self,env_path:Path)->Optional[str]:
        config_file=env_path/'.pyrunner'/'config.json'
        if not config_file.exists():return None
        try:
            with open(config_file,'r')as f:metadata=json.load(f)
            return metadata.get('config_hash')
        except:return None
    def _needs_dependency_update(self,env_path:Path,config:Dict)->Tuple[bool,Set[str]]:
        if not env_path.exists():return True,set(config['dependencies'])
        current_hash=self._get_config_hash(config);stored_hash=self._get_stored_config_hash(env_path)
        if current_hash==stored_hash:return False,set()
        lock_file=env_path/'.pyrunner'/'requirements.lock'
        if not lock_file.exists():return True,set(config['dependencies'])
        try:
            with open(lock_file,'r')as f:lock_data=json.load(f)
            installed={e['name'].lower():e['version'] for e in lock_data['entries']};changed=set()
            for dep in config['dependencies']:
                dep_name=dep.split('>=')[0].split('==')[0].split('<')[0].strip().lower()
                if dep_name not in installed:changed.add(dep)
            return len(changed)>0,changed
        except:return True,set(config['dependencies'])
    def validate_environment(self,env_path:Path)->Tuple[bool,List[str]]:
        issues=[]
        if not env_path.exists():issues.append("Environment directory does not exist");return False,issues
        python_path=self.get_python_path(env_path)
        if not python_path.exists():issues.append("Python executable not found")
        pip_path=self.get_pip_path(env_path)
        if not pip_path.exists():issues.append("Pip executable not found")
        pyrunner_dir=env_path/'.pyrunner'
        if not pyrunner_dir.exists():issues.append("PyRunner metadata directory missing")
        try:
            r=subprocess.run([str(python_path),"-c","import sys; print(sys.version)"],capture_output=True,text=True,timeout=10)
            if r.returncode!=0:issues.append("Python executable is corrupted or non-functional")
        except:issues.append("Failed to test Python executable")
        if len(issues)==0:
            if self.logger:self.logger.info("Environment validation passed")
            return True,[]
        else:
            if self.logger:self.logger.warning(f"Environment validation failed: {', '.join(issues)}")
            return False,issues
    def create_virtual_environment(self,env_path:Path,python_version:Optional[str]=None)->None:
        if env_path.exists():
            is_valid,issues=self.validate_environment(env_path)
            if is_valid:
                if self.logger:self.logger.info(f"Virtual environment already exists and is valid: {env_path}")
                return
            else:
                if self.logger:self.logger.warning(f"Existing environment is corrupted, recreating: {', '.join(issues)}")
                shutil.rmtree(env_path)
        try:
            if self.logger:self.logger.info(f"Creating virtual environment: {env_path}")
            venv.create(env_path,with_pip=True);pyrunner_dir=env_path/'.pyrunner';pyrunner_dir.mkdir(exist_ok=True)
            metadata={'created_at':time.time(),'python_version':python_version,'pyrunner_version':'2.0.0','config_hash':None,'scripts':[],'last_used':time.time()}
            with open(pyrunner_dir/'config.json','w')as f:json.dump(metadata,f,indent=2)
            if self.logger:self.logger.info(f"Virtual environment created successfully: {env_path}")
        except Exception as e:raise PyRunnerError(f"Failed to create virtual environment: {e}")
    def get_pip_path(self,env_path:Path)->Path:
        if sys.platform=="win32":return env_path/"Scripts"/"pip.exe"
        else:return env_path/"bin"/"pip"
    def get_python_path(self,env_path:Path)->Path:
        if sys.platform=="win32":return env_path/"Scripts"/"python.exe"
        else:return env_path/"bin"/"python"
    def _update_config_hash(self,env_path:Path,config:Dict)->None:
        config_file=env_path/'.pyrunner'/'config.json'
        if config_file.exists():
            with open(config_file,'r')as f:metadata=json.load(f)
        else:
            metadata={'created_at':time.time(),'python_version':config.get('python_version'),'pyrunner_version':'2.0.0','scripts':[]}
        metadata['config_hash']=self._get_config_hash(config);metadata['last_updated']=time.time();metadata['last_used']=time.time()
        with open(config_file,'w')as f:json.dump(metadata,f,indent=2)
    def _update_script_usage(self,env_path:Path,script_path:str)->None:
        config_file=env_path/'.pyrunner'/'config.json'
        if not config_file.exists():return
        with open(config_file,'r')as f:metadata=json.load(f)
        scripts=metadata.get('scripts',[]);name=Path(script_path).name
        if name not in scripts:scripts.append(name);metadata['scripts']=scripts
        metadata['last_used']=time.time()
        with open(config_file,'w')as f:json.dump(metadata,f,indent=2)
    def install_dependencies_parallel(self,env_path:Path,dependencies:List[str])->List[str]:
        pip_path=self.get_pip_path(env_path);failed=[]
        def install_package(dep):
            try:
                r=subprocess.run([str(pip_path),"install","--upgrade",dep],capture_output=True,text=True,timeout=300)
                if r.returncode!=0:return dep
                return None
            except:return dep
        if len(dependencies)<=3:
            for d in dependencies:
                f=install_package(d)
                if f:failed.append(f)
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=3)as ex:
                fut={ex.submit(install_package,d):d for d in dependencies}
                for x in concurrent.futures.as_completed(fut):
                    f=x.result()
                    if f:failed.append(f)
        return failed
    def install_dependencies(self,env_path:Path,config:Dict,force_update:bool=False)->None:
        needs_update,changed=self._needs_dependency_update(env_path,config)
        if not force_update and not needs_update:
            if self.logger:self.logger.info("Dependencies are up to date, skipping installation")
            return
        pip_path=self.get_pip_path(env_path)
        if not pip_path.exists():raise PyRunnerError(f"Pip not found in virtual environment: {pip_path}")
        try:
            if self.logger:
                if force_update:self.logger.info("Force updating all dependencies...")
                else:self.logger.info(f"Updating {len(changed)} changed dependencies...")
            subprocess.run([str(pip_path),"install","--upgrade","pip"],check=True,capture_output=True,text=True)
            if not force_update and self.install_from_lock_file(env_path):deps=list(changed) if changed else []
            else:deps=config['dependencies'].copy()
            if config['requirements_file'] and config['config_type']=='yaml':
                req=Path(config['requirements_file'])
                if req.exists():
                    if self.logger:self.logger.info(f"Installing from requirements file: {req}")
                    subprocess.run([str(pip_path),"install","-r",str(req)],check=True,capture_output=True,text=True)
            if deps:
                if self.logger:self.logger.info(f"Installing {len(deps)} dependencies in parallel...")
                failed=self.install_dependencies_parallel(env_path,deps)
                if failed:
                    msg=f"Failed to install dependencies: {', '.join(failed)}";raise PyRunnerError(self.enhanced_error_message(Exception(msg),str(env_path)))
            if config['dev_dependencies']:
                if self.logger:self.logger.info(f"Installing {len(config['dev_dependencies'])} dev dependencies...")
                failed_dev=self.install_dependencies_parallel(env_path,config['dev_dependencies'])
                if failed_dev and self.logger:self.logger.warning(f"Failed to install dev dependencies: {', '.join(failed_dev)}")
            self.generate_lock_file(env_path,config);self._update_config_hash(env_path,config)
            if self.logger:self.logger.info("Dependencies installation/update completed")
        except subprocess.CalledProcessError as e:raise PyRunnerError(self.enhanced_error_message(e,str(env_path)))
    def get_environment_info(self,env_path:Path)->Optional[EnvironmentInfo]:
        if not env_path.exists():return None
        config_file=env_path/'.pyrunner'/'config.json'
        if not config_file.exists():return None
        try:
            with open(config_file,'r')as f:metadata=json.load(f)
            def get_folder_size(p):
                t=0
                try:
                    for dp,dn,fn in os.walk(p):
                        for x in fn:
                            fp=os.path.join(dp,x)
                            if os.path.exists(fp):t+=os.path.getsize(fp)
                except:pass
                return t/(1024*1024)
            lock_file=env_path/'.pyrunner'/'requirements.lock';dep_count=0
            if lock_file.exists():
                with open(lock_file,'r')as f:l=json.load(f);dep_count=len(l.get('entries',[]))
            return EnvironmentInfo(name=env_path.name,path=str(env_path),created_at=metadata.get('created_at',time.time()),last_used=metadata.get('last_used',time.time()),scripts=metadata.get('scripts',[]),size_mb=get_folder_size(env_path),python_version=metadata.get('python_version','unknown'),dependency_count=dep_count)
        except:return None
    def list_environments(self)->List[EnvironmentInfo]:
        envs=[];cur=Path.cwd()
        for item in cur.iterdir():
            if item.is_dir() and (item/'.pyrunner').exists():
                info=self.get_environment_info(item)
                if info:envs.append(info)
        return sorted(envs,key=lambda x:x.last_used,reverse=True)
    def cleanup_unused_environments(self,days_threshold:int=30)->List[str]:
        th=time.time()-(days_threshold*24*60*60);cleaned=[]
        for info in self.list_environments():
            if info.last_used<th:
                try:
                    p=Path(info.path);shutil.rmtree(p);cleaned.append(info.name)
                    if self.logger:self.logger.info(f"Cleaned up unused environment: {info.name}")
                except Exception as e:
                    if self.logger:self.logger.error(f"Failed to cleanup {info.name}: {e}")
        return cleaned
    def run_script_with_watch(self,script_path:str,env_path:Path,config_path:str,extra_args:List[str]=None,env_vars:Dict=None)->None:
        print(f"🔍 Starting file watcher for: {script_path}");print("💡 Press Ctrl+C to stop watching")
        fw=FileWatcher(self,script_path,env_path,extra_args,env_vars,config_path);obs=Observer();sd=Path(script_path).parent;obs.schedule(fw,str(sd),recursive=False);obs.start()
        try:
            fw._restart_script()
            while True:time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️  Stopping file watcher...")
            if fw.process and fw.process.poll() is None:fw.process.terminate();fw.process.wait()
        finally:
            obs.stop();obs.join();print("✅ File watcher stopped")
    def run_script(self,script_path:str,env_path:Path,extra_args:List[str]=None,run_in_background:bool=False,env_vars:Dict=None)->Optional[int]:
        sf=Path(script_path)
        if not sf.exists():raise PyRunnerError(self.enhanced_error_message(Exception(f"Script file not found: {script_path}"),script_path))
        py=self.get_python_path(env_path)
        if not py.exists():raise PyRunnerError(self.enhanced_error_message(Exception(f"Python executable not found in virtual environment: {py}"),str(env_path)))
        self._update_script_usage(env_path,script_path);cmd=[str(py),str(sf)]
        if extra_args:cmd.extend(extra_args)
        env=os.environ.copy()
        if env_vars:env.update(env_vars)
        if self.logger:
            self.logger.info(f"Running script: {' '.join(cmd)}")
            if env_vars:self.logger.info(f"Environment variables: {list(env_vars.keys())}")
        try:
            if run_in_background:return self._run_background_process(cmd,env,env_path)
            else:return self._run_foreground_process(cmd,env)
        except Exception as e:raise PyRunnerError(self.enhanced_error_message(e,script_path))
    def _run_foreground_process(self,cmd:List[str],env:Dict)->int:
        if self.logger:self.logger.info("Running in foreground mode")
        p=subprocess.Popen(cmd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
        for line in p.stdout:
            print(line,end='')
            if self.logger:self.logger.info(f"SCRIPT OUTPUT: {line.strip()}")
        p.wait()
        if self.logger:self.logger.info(f"Script finished with return code: {p.returncode}")
        return p.returncode
    def _run_background_process(self,cmd:List[str],env:Dict,env_path:Path)->int:
        if self.logger:self.logger.info("Running in background mode")
        p=subprocess.Popen(cmd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,start_new_session=True)
        pid_file=env_path/'.pyrunner'/'process.pid'
        with open(pid_file,'w')as f:f.write(str(p.pid))
        if self.logger:self.logger.info(f"Background process started with PID: {p.pid}");self.logger.info(f"PID saved to: {pid_file}")
        print(f"Process started in background with PID: {p.pid}");print(f"PID file: {pid_file}")
        if self.logger and self.log_file:
            def log_output():
                for line in p.stdout:self.logger.info(f"SCRIPT OUTPUT: {line.strip()}")
            threading.Thread(target=log_output,daemon=True).start()
        return p.pid
    def reset_environment(self,env_path:Path)->None:
        if not env_path.exists():raise PyRunnerError(f"Environment not found: {env_path}")
        try:
            if self.logger:self.logger.info(f"Resetting environment: {env_path}")
            shutil.rmtree(env_path)
            if self.logger:self.logger.info(f"Environment deleted: {env_path}")
            print(f"Environment reset: {env_path}")
        except Exception as e:raise PyRunnerError(f"Failed to reset environment: {e}")
    def parse_extra_args(self,extra_args_string:str)->List[str]:
        if not extra_args_string:return []
        s=extra_args_string.strip()
        if s.startswith('[') and s.endswith(']'):s=s[1:-1]
        try:return shlex.split(s)
        except ValueError as e:raise PyRunnerError(f"Invalid extra arguments format: {e}")
def create_pyrunner_gui_yaml(dst: str|Path=None)->Path:
    root=Path(__file__).resolve().parent
    cfg=Path(dst) if dst else root/"pyrunner_gui.yaml"
    content=("python_version: null\n"
             "dependencies:\n"
             "  - PyQt6\n"
             "  - PyYAML\n"
             "  - watchdog\n"
             "dev_dependencies: []\n"
             "environment_variables: {}\n"
             "profiles: {}\n"
             "active_profile: default\n"
             "hot_reload: false\n"
             "template: null\n")
    cfg.write_text(content,encoding="utf-8")
    print(f"✅ Created {cfg}")
    return cfg
def _ensure_gui_env_and_config():
    root=Path(__file__).resolve().parent
    env=root/"pyrunner_gui_env"
    cfg=root/"pyrunner_gui.yaml"
    runner=PyRunner()
    if not cfg.exists():create_pyrunner_gui_yaml(cfg)
    if not env.exists():runner.create_virtual_environment(env,None)
    config={'python_version':None,'requirements_file':None,'dependencies':['PyQt6','PyYAML','watchdog'],'dev_dependencies':[],'environment_variables':{},'config_type':'requirements','profiles':{},'active_profile':'default','hot_reload':False,'template':None}
    runner.install_dependencies(env,config)
    return env
def launch_gui():
    env=_ensure_gui_env_and_config()
    p=Path(__file__).with_name("pyrunner_gui.py")
    if not p.exists():
        print("❌ GUI entry 'pyrunner_gui.py' not found")
        return 1
    py=PyRunner().get_python_path(env)
    _spin_sleep("Launching GUI...",1.2)
    r=subprocess.run([str(py),str(p)])
    return r.returncode
def _maybe_launch_gui():
    args=set(sys.argv[1:])
    if any(x in args for x in ("-G","-g","--GUI","--gui")):return launch_gui()
    return None
def new_mode_entry()->int:
    _spin_sleep("Getting things ready...",2.8)
    print("✅ Ready")
    return 0
def main():
    parser=argparse.ArgumentParser(description="PyRunner - Advanced Python Virtual Environment Manager",formatter_class=argparse.RawDescriptionHelpFormatter,epilog="""
Examples:
  %(prog)s run script.py                           # Smart run with auto-detection
  %(prog)s run script.py --watch                   # Run with hot reloading
  %(prog)s install flask                           # Add package to current env
  %(prog)s shell my_env                           # Launch shell in environment
  %(prog)s doctor                                 # Diagnose all environments
  %(prog)s -f app.py -c config.yaml --env shared  # Traditional usage
        """)
    parser.add_argument('-n','--new',action='store_true',help='First-time quick start with spinner')
    subparsers=parser.add_subparsers(dest='command',help='Quick commands')
    run_parser=subparsers.add_parser('run',help='Run script with smart defaults')
    run_parser.add_argument('script',help='Python script to run')
    run_parser.add_argument('--watch',action='store_true',help='Enable hot reloading')
    run_parser.add_argument('--env',help='Environment to use')
    run_parser.add_argument('--profile',help='Configuration profile to use')
    run_parser.add_argument('packages',nargs='*',help='Packages to install if no config found')
    install_parser=subparsers.add_parser('install',help='Add package to environment')
    install_parser.add_argument('package',help='Package to install')
    install_parser.add_argument('--env',help='Environment to use (default: current directory env)')
    remove_parser=subparsers.add_parser('remove',help='Remove package from environment')
    remove_parser.add_argument('package',help='Package to remove')
    remove_parser.add_argument('--env',help='Environment to use (default: current directory env)')
    shell_parser=subparsers.add_parser('shell',help='Launch shell in environment')
    shell_parser.add_argument('env',help='Environment name')
    doctor_parser=subparsers.add_parser('doctor',help='Diagnose environment issues')
    doctor_parser.add_argument('env',nargs='?',help='Specific environment to check')
    parser.add_argument('-f','--file',type=str,help='Python script to run')
    parser.add_argument('-c','--config',type=str,help='Configuration file (requirements.txt or .yaml)')
    parser.add_argument('-l','--location',type=str,help='Virtual environment folder name (deprecated, use --env)')
    parser.add_argument('--env',type=str,help='Virtual environment path (can be shared between scripts)')
    parser.add_argument('-p','--pid',action='store_true',help='Run as background process with PID tracking')
    parser.add_argument('-e','--extra',type=str,help='Arguments to pass to target script (e.g., "[-p 8000 --debug]")')
    parser.add_argument('--log',nargs='*',metavar=('LOCATION','FILENAME'),help='Enable logging: --log [location] [filename]')
    parser.add_argument('--watch',action='store_true',help='Enable hot reloading (restart on file changes)')
    parser.add_argument('--watch-deps',action='store_true',help='Watch dependency files for changes')
    parser.add_argument('--reset',type=str,metavar='LOCATION',help='Reset virtual environment at specified location')
    parser.add_argument('--force-update',action='store_true',help='Force update dependencies even if they appear unchanged')
    parser.add_argument('--list-envs',action='store_true',help='List all PyRunner environments')
    parser.add_argument('--cleanup-envs',type=int,metavar='DAYS',help='Cleanup environments unused for specified days')
    parser.add_argument('--clone-env',nargs=2,metavar=('SOURCE','TARGET'),help='Clone environment from source to target')
    parser.add_argument('--validate-env',type=str,metavar='ENV_PATH',help='Validate environment integrity')
    parser.add_argument('--fix-env',type=str,metavar='ENV_PATH',help='Auto-fix environment issues')
    parser.add_argument('--health-check',action='store_true',help='Check health of all environments')
    parser.add_argument('--debug',action='store_true',help='Enable debug mode with verbose error messages')
    parser.add_argument('--version',action='version',version='PyRunner 2.0.0')
    args=parser.parse_args()
    runner=PyRunner()
    try:
        if args.new or (_is_first_run() and not args.command and not args.file and not args.config):
            return new_mode_entry()
        if args.command=='run':
            config_path=runner.smart_auto_detect_config(args.script)
            if not config_path and args.packages:config_path=runner.create_quick_config(args.script,args.packages)
            elif not config_path:
                print("❌ No configuration file found and no packages specified");print("💡 Create requirements.txt or specify packages: pyrunner run script.py flask requests");return 1
            script_name=Path(args.script).stem;env_path=Path(args.env or f"{script_name}_env");config=runner.parse_config(config_path)
            if args.profile and args.profile in config.get('profiles',{}):config['active_profile']=args.profile
            runner.create_virtual_environment(env_path,config['python_version']);runner.install_dependencies(env_path,config)
            if args.watch:runner.run_script_with_watch(args.script,env_path,config_path,env_vars=config['environment_variables'])
            else:return runner.run_script(args.script,env_path,env_vars=config['environment_variables'])
        elif args.command=='install':
            env_path=Path(args.env or 'current_env')
            if not env_path.exists():
                print(f"❌ Environment not found: {env_path}");print("💡 Create environment first or specify existing one with --env");return 1
            runner.add_package_to_env(env_path,args.package);return 0
        elif args.command=='remove':
            env_path=Path(args.env or 'current_env')
            if not env_path.exists():print(f"❌ Environment not found: {env_path}");return 1
            runner.remove_package_from_env(env_path,args.package);return 0
        elif args.command=='shell':
            env_path=Path(args.env);runner.launch_shell(env_path);return 0
        elif args.command=='doctor':
            issues=runner.doctor_diagnose(Path(args.env)) if args.env else runner.doctor_diagnose()
            print("🏥 PyRunner Health Check");print("="*50)
            if issues['critical']:
                print("🚨 Critical Issues:");[print(f"   • {i}") for i in issues['critical']]
            if issues['warnings']:
                print("\n⚠️  Warnings:");[print(f"   • {w}") for w in issues['warnings']]
            if issues['suggestions']:
                print("\n💡 Suggestions:");[print(f"   • {s}") for s in issues['suggestions']]
            if not any(issues.values()):print("✅ All environments are healthy!")
            return 0
        if args.health_check:
            issues=runner.doctor_diagnose()
            if any(issues.values()):print("⚠️  Issues found. Run 'pyrunner doctor' for details.");return 1
            else:print("✅ All environments are healthy!");return 0
        if args.fix_env:
            env_path=Path(args.fix_env);success=runner.auto_fix_environment(env_path);return 0 if success else 1
        if args.list_envs:
            environments=runner.list_environments()
            if not environments:print("No PyRunner environments found.");return 0
            print(f"\n{'Name':<20} {'Size (MB)':<10} {'Dependencies':<12} {'Scripts':<8} {'Last Used':<12}");print("-"*75)
            for env in environments:
                last_used=datetime.fromtimestamp(env.last_used).strftime('%Y-%m-%d');scripts_count=len(env.scripts);print(f"{env.name:<20} {env.size_mb:<10.1f} {env.dependency_count:<12} {scripts_count:<8} {last_used:<12}")
            return 0
        if args.cleanup_envs is not None:
            cleaned=runner.cleanup_unused_environments(args.cleanup_envs)
            if cleaned:print(f"Cleaned up {len(cleaned)} unused environments: {', '.join(cleaned)}")
            else:print(f"No environments found unused for more than {args.cleanup_envs} days.")
            return 0
        if args.clone_env:
            source_env=Path(args.clone_env[0]);target_env=Path(args.clone_env[1]);runner.clone_environment(source_env,target_env);print(f"Environment cloned from {source_env} to {target_env}");return 0
        if args.validate_env:
            env_path=Path(args.validate_env);is_valid,issues=runner.validate_environment(env_path)
            if is_valid:
                print(f"✅ Environment {env_path} is valid and healthy.");env_info=runner.get_environment_info(env_path)
                if env_info:
                    print(f"   Size: {env_info.size_mb:.1f} MB");print(f"   Dependencies: {env_info.dependency_count}");print(f"   Scripts: {len(env_info.scripts)} ({', '.join(env_info.scripts) if env_info.scripts else 'none'})");print(f"   Last used: {datetime.fromtimestamp(env_info.last_used).strftime('%Y-%m-%d %H:%M')}")
            else:
                print(f"❌ Environment {env_path} has issues:");[print(f"   • {i}") for i in issues];return 1
            return 0
        if args.reset:
            env_path=Path(args.reset);runner.reset_environment(env_path);return 0
        if not args.file or not args.config:parser.error("Both -f/--file and -c/--config are required for traditional mode")
        log_location=None;log_filename=None
        if args.log is not None:
            if len(args.log)>=1:log_location=args.log[0]
            if len(args.log)>=2:log_filename=args.log[1]
            elif len(args.log)==0:log_location='./logs/'
        script_name=Path(args.file).stem
        if log_location:runner.setup_logging(log_location,log_filename,script_name)
        if args.env:env_path=Path(args.env)
        elif args.location:env_path=Path(args.location)
        else:env_name=f"{script_name}_env";env_path=Path(env_name)
        if runner.logger:runner.logger.info(f"Starting PyRunner for script: {args.file}");runner.logger.info(f"Environment path: {env_path}")
        config=runner.parse_config(args.config)
        if config.get('template'):
            template_path=Path(config['template'])
            if template_path.exists():
                if runner.logger:runner.logger.info(f"Using template: {template_path}")
                runner.clone_environment(template_path,env_path)
        runner.create_virtual_environment(env_path,config['python_version']);runner.install_dependencies(env_path,config,args.force_update)
        extra_args=runner.parse_extra_args(args.extra) if args.extra else []
        if args.watch or args.watch_deps:
            runner.run_script_with_watch(args.file,env_path,args.config,extra_args,config['environment_variables']);return 0
        result=runner.run_script(args.file,env_path,extra_args,args.pid,config['environment_variables'])
        if not args.pid:return result if result is not None else 0
        else:return 0
    except PyRunnerError as e:
        if args.debug:print(str(e))
        else:
            error_lines=str(e).split('\n');print(error_lines[0])
            if len(error_lines)>1:print("💡 Run with --debug for detailed suggestions")
        return 1
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user");return 1
    except Exception as e:
        if args.debug:
            import traceback;print(f"💥 Unexpected error: {e}");traceback.print_exc()
        else:
            print(f"💥 Unexpected error: {e}");print("💡 Run with --debug for full traceback")
        return 1
if __name__=="__main__":
    code=_maybe_launch_gui()
    if code is not None:sys.exit(code)
    sys.exit(main())
