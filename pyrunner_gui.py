import sys,os,subprocess,threading,json
from pathlib import Path
from PyQt6.QtCore import Qt,QTimer,pyqtSignal,QThread
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QProgressBar,QPushButton,QFileDialog,QLineEdit,QTextEdit,QCheckBox,QTableWidget,QTableWidgetItem,QHeaderView,QComboBox,QSplitter,QStackedWidget,QDialog,QPlainTextEdit,QMessageBox,QFormLayout
from pyrunner import PyRunner
APP_NAME="PyRunner GUI V2";APP_VER="";GUI_ENV_NAME="pyrunner_gui_env"
class ProcThread(QThread):
    line=pyqtSignal(str);finished=pyqtSignal(int)
    def __init__(self,cmd,cwd=None,env=None):super().__init__();self.cmd=cmd;self.cwd=cwd;self.env=env;self.p=None
    def run(self):
        try:
            self.p=subprocess.Popen(self.cmd,cwd=self.cwd,env=self.env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
            for l in self.p.stdout:self.line.emit(l.rstrip("\n"))
            self.p.wait();self.finished.emit(self.p.returncode)
        except Exception as e:self.line.emit(f"[ERR] {e}");self.finished.emit(1)
    def stop(self):
        try:
            if self.p and self.p.poll() is None:self.p.terminate()
        except:pass
class Spinner:
    def __init__(self,bar:QProgressBar,label:QLabel):self.bar=bar;self.label=label;self.t=QTimer();self.t.setInterval(80);self.frames="⠋⠙⠸⠴⠦⠇";self.i=0;self.msg=""
    def start(self,msg):self.msg=msg;self.label.setText(msg);self.bar.setRange(0,0);self.t.timeout.connect(self._tick);self.t.start()
    def _tick(self):self.i=(self.i+1)%len(self.frames);self.label.setText(f"{self.msg}  {self.frames[self.i]}")
    def stop(self,ok=True):self.t.stop();self.bar.setRange(0,1);self.bar.setValue(1 if ok else 0)
class ConfigMakerDialog(QDialog):
    def __init__(self,parent=None,seed_yaml:str|None=None):
        super().__init__(parent);self.setWindowTitle("Config Maker");self.resize(760,640)
        v=QVBoxLayout(self);f=QFormLayout();v.addLayout(f)
        self.lePy=QLineEdit();self.leDeps=QLineEdit();self.leDevDeps=QLineEdit();self.leEnv=QLineEdit();self.leActive=QLineEdit();self.cbHot=QCheckBox("Enable hot reload");self.leTpl=QLineEdit();self.leReq=QLineEdit()
        self.leDevDeps.setPlaceholderText("pkg1,pkg2>=1.0");self.leDeps.setPlaceholderText("pkg1,pkg2>=1.0");self.leEnv.setPlaceholderText("KEY1=VAL1,KEY2=VAL2");self.leActive.setPlaceholderText("development/testing/production");self.leTpl.setPlaceholderText("./templates/web_template");self.leReq.setPlaceholderText("./requirements.txt")
        f.addRow("Python version",self.lePy);f.addRow("Dependencies",self.leDeps);f.addRow("Dev dependencies",self.leDevDeps);f.addRow("Environment variables",self.leEnv);f.addRow("Active profile",self.leActive);f.addRow("",self.cbHot);f.addRow("Template path",self.leTpl);f.addRow("Requirements file",self.leReq)
        g=QLabel("Profiles");v.addWidget(g)
        pf=QFormLayout();v.addLayout(pf)
        self.leDevPDeps=QLineEdit();self.leDevPEnv=QLineEdit();self.leTestPDeps=QLineEdit();self.leTestPEnv=QLineEdit();self.leProdPDeps=QLineEdit();self.leProdPEnv=QLineEdit()
        self.leDevPDeps.setPlaceholderText("flask[dev],pytest,black");self.leDevPEnv.setPlaceholderText("DEBUG=true,LOG_LEVEL=debug,DATABASE_URL=sqlite:///dev.db")
        self.leTestPDeps.setPlaceholderText("flask,pytest,coverage,pytest-cov");self.leTestPEnv.setPlaceholderText("TESTING=true,DATABASE_URL=sqlite:///:memory:")
        self.leProdPDeps.setPlaceholderText("flask,gunicorn,psycopg2-binary,redis");self.leProdPEnv.setPlaceholderText("DEBUG=false,LOG_LEVEL=info,DATABASE_URL=postgresql://prod/mydb")
        pf.addRow("development deps",self.leDevPDeps);pf.addRow("development env",self.leDevPEnv);pf.addRow("testing deps",self.leTestPDeps);pf.addRow("testing env",self.leTestPEnv);pf.addRow("production deps",self.leProdPDeps);pf.addRow("production env",self.leProdPEnv)
        b=QHBoxLayout();self.btnLoad=QPushButton("Load from file");self.btnValidate=QPushButton("Validate");self.btnSaveAs=QPushButton("Save As YAML");self.btnOK=QPushButton("Apply");self.btnClose=QPushButton("Close");b.addWidget(self.btnLoad);b.addStretch(1);b.addWidget(self.btnValidate);b.addWidget(self.btnSaveAs);b.addWidget(self.btnOK);b.addWidget(self.btnClose);v.addLayout(b)
        self.btnClose.clicked.connect(self.close);self.btnOK.clicked.connect(self._apply);self.btnSaveAs.clicked.connect(self._saveas);self.btnValidate.clicked.connect(self._validate);self.btnLoad.clicked.connect(self._load_file)
        self._style()
        self.result_yaml=None
        if seed_yaml:self._load_from_yaml_text(seed_yaml)
    def _style(self):
        self.setStyleSheet("*{font-family:Inter,Arial,Segoe UI,Roboto,Helvetica,system-ui,sans-serif;font-size:13px} QDialog{background:#0f1115;color:#e6e6e6} QLineEdit{background:#121621;color:#e6e6e6;border:1px solid #2a2f3a;border-radius:8px;padding:8px} QLabel{color:#cfd3dc} QCheckBox{color:#e6e6e6} QPushButton{background:#1b1f2a;color:#e6e6e6;border:1px solid #2a2f3a;border-radius:10px;padding:8px 14px} QPushButton:hover{background:#222736}")
    def _csv(self,s):return [x.strip() for x in s.split(",") if x.strip()]
    def _kv(self,s):
        d={}
        for p in self._csv(s):
            if "=" in p:
                k,v=p.split("=",1);d[k.strip()]=v.strip()
        return d
    def _join_csv(self,seq):return ",".join(seq or [])
    def _join_kv(self,d):return ",".join([f"{k}={v}" for k,v in (d or {}).items()])
    def _build_yaml_dict(self):
        import yaml
        y={}
        if self.lePy.text().strip():y["python_version"]=self.lePy.text().strip()
        if self.leDeps.text().strip():y["dependencies"]=self._csv(self.leDeps.text())
        if self.leDevDeps.text().strip():y["dev_dependencies"]=self._csv(self.leDevDeps.text())
        if self.leEnv.text().strip():y["environment_variables"]=self._kv(self.leEnv.text())
        pr={}
        if any([self.leDevPDeps.text().strip(),self.leDevPEnv.text().strip()]):pr["development"]={"dependencies":self._csv(self.leDevPDeps.text()),"env_vars":self._kv(self.leDevPEnv.text())}
        if any([self.leTestPDeps.text().strip(),self.leTestPEnv.text().strip()]):pr["testing"]={"dependencies":self._csv(self.leTestPDeps.text()),"env_vars":self._kv(self.leTestPEnv.text())}
        if any([self.leProdPDeps.text().strip(),self.leProdPEnv.text().strip()]):pr["production"]={"dependencies":self._csv(self.leProdPDeps.text()),"env_vars":self._kv(self.leProdPEnv.text())}
        if pr:y["profiles"]=pr
        if self.leActive.text().strip():y["active_profile"]=self.leActive.text().strip()
        y["hot_reload"]=bool(self.cbHot.isChecked())
        if self.leTpl.text().strip():y["template"]=self.leTpl.text().strip()
        if self.leReq.text().strip():y["requirements_file"]=self.leReq.text().strip()
        return y
    def _validate(self):
        import yaml
        try:yaml.safe_dump(self._build_yaml_dict(),sort_keys=False);QMessageBox.information(self,"YAML","Valid.")
        except Exception as e:QMessageBox.critical(self,"YAML",str(e))
    def _apply(self):
        import yaml
        try:self.result_yaml=yaml.safe_dump(self._build_yaml_dict(),sort_keys=False);self.accept()
        except Exception as e:QMessageBox.critical(self,"YAML",str(e))
    def _saveas(self):
        import yaml
        p,_=QFileDialog.getSaveFileName(self,"Save YAML",str(Path.cwd()),"YAML (*.yaml *.yml)")
        if not p:return
        Path(p).write_text(yaml.safe_dump(self._build_yaml_dict(),sort_keys=False),encoding="utf-8");QMessageBox.information(self,"Saved",p)
    def _load_file(self):
        p,_=QFileDialog.getOpenFileName(self,"Open YAML",str(Path.cwd()),"YAML (*.yaml *.yml)")
        if not p:return
        self._load_from_yaml_text(Path(p).read_text(encoding="utf-8"))
    def _load_from_yaml_text(self,text):
        import yaml
        try:
            y=yaml.safe_load(text) or {}
            self.lePy.setText(str(y.get("python_version","") or ""))
            self.leDeps.setText(self._join_csv(y.get("dependencies") or []))
            self.leDevDeps.setText(self._join_csv(y.get("dev_dependencies") or []))
            self.leEnv.setText(self._join_kv(y.get("environment_variables") or {}))
            self.leActive.setText(str(y.get("active_profile","") or ""))
            self.cbHot.setChecked(bool(y.get("hot_reload",False)))
            self.leTpl.setText(str(y.get("template","") or ""))
            self.leReq.setText(str(y.get("requirements_file","") or ""))
            p=y.get("profiles") or {}
            d=p.get("development") or {};t=p.get("testing") or {};r=p.get("production") or {}
            self.leDevPDeps.setText(self._join_csv((d.get("dependencies") or [])));self.leDevPEnv.setText(self._join_kv(d.get("env_vars") or {}))
            self.leTestPDeps.setText(self._join_csv((t.get("dependencies") or [])));self.leTestPEnv.setText(self._join_kv(t.get("env_vars") or {}))
            self.leProdPDeps.setText(self._join_csv((r.get("dependencies") or [])));self.leProdPEnv.setText(self._join_kv(r.get("env_vars") or {}))
        except Exception as e:QMessageBox.critical(self,"YAML",str(e))
class Main(QMainWindow):
    def __init__(self):
        super().__init__();self.setWindowTitle(APP_NAME);self.resize(1000,660);self.runner=PyRunner();self.proc=None;self.advanced=False;self._ui();self._style();self._center();QTimer.singleShot(80,self._list_envs)
    def _ui(self):
        w=QWidget();root=QVBoxLayout(w);root.setContentsMargins(16,16,16,16);root.setSpacing(10)
        top=QHBoxLayout();title=QLabel(APP_NAME);title.setFont(QFont("Arial",18,QFont.Weight.DemiBold));ver=QLabel(APP_VER);ver.setStyleSheet("opacity:.6")
        self.btnConfigMaker=QPushButton("Config Maker");self.btnConfigMaker.clicked.connect(self._open_config_maker)
        self.btnToggle=QPushButton("Switch to Advanced");self.btnToggle.clicked.connect(self._toggle_view)
        top.addWidget(title);top.addStretch(1);top.addWidget(ver);top.addSpacing(12);top.addWidget(self.btnConfigMaker);top.addWidget(self.btnToggle)
        self.stack=QStackedWidget()
        self.pageNormal=self._build_normal()
        self.pageAdvanced=self._build_advanced()
        self.stack.addWidget(self.pageNormal);self.stack.addWidget(self.pageAdvanced);self.stack.setCurrentIndex(0)
        root.addLayout(top);root.addWidget(self.stack,1);self.setCentralWidget(w)
    def _build_normal(self):
        p=QWidget();v=QVBoxLayout(p);v.setContentsMargins(0,0,0,0);v.setSpacing(10)
        box=QHBoxLayout()
        self.nScript=QLineEdit();btnNS=QPushButton("Script");btnNS.clicked.connect(lambda:self._pick(self.nScript,"Choose script","Python (*.py)"))
        self.nConfig=QLineEdit();btnNC=QPushButton("Config");btnNC.clicked.connect(lambda:self._pick(self.nConfig,"Choose config","Config (requirements.txt *.yaml *.yml)"))
        btnAuto=QPushButton("Auto-Detect");btnAuto.clicked.connect(self._normal_autodetect)
        box.addWidget(QLabel("Script"));box.addWidget(self.nScript,3);box.addWidget(btnNS);box.addSpacing(8);box.addWidget(QLabel("Config"));box.addWidget(self.nConfig,3);box.addWidget(btnNC);box.addWidget(btnAuto)
        act=QHBoxLayout()
        self.btnEasyStart=QPushButton("Easy Start");self.btnEasyStart.clicked.connect(self._easy_start)
        self.btnNormalStop=QPushButton("Stop");self.btnNormalStop.clicked.connect(self._stop);self.btnNormalStop.setEnabled(False)
        self.btnRefresh=QPushButton("Refresh Envs");self.btnRefresh.clicked.connect(self._list_envs)
        act.addWidget(self.btnEasyStart);act.addWidget(self.btnNormalStop);act.addStretch(1);act.addWidget(self.btnRefresh)
        split=QSplitter()
        left=QWidget();lv=QVBoxLayout(left);lv.setContentsMargins(0,0,0,0);lv.setSpacing(8)
        self.tbl=QTableWidget(0,5);self.tbl.setHorizontalHeaderLabels(["Name","Path","Size(MB)","Deps","Scripts"]);self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch);self.tbl.verticalHeader().setVisible(False);self.tbl.setSelectionBehavior(self.tbl.SelectionBehavior.SelectRows)
        lv.addWidget(self.tbl)
        right=QWidget();rv=QVBoxLayout(right);rv.setContentsMargins(0,0,0,0);rv.setSpacing(8)
        self.console=QTextEdit();self.console.setReadOnly(True);rv.addWidget(self.console,1)
        bbar=QHBoxLayout();self.lblSpin=QLabel("");self.bar=QProgressBar();self.bar.setFixedHeight(6);self.bar.setTextVisible(False);self.spin=Spinner(self.bar,self.lblSpin);bbar.addWidget(self.lblSpin);bbar.addWidget(self.bar,1);rv.addLayout(bbar)
        split.addWidget(left);split.addWidget(right);split.setStretchFactor(0,1);split.setStretchFactor(1,2)
        v.addLayout(box);v.addLayout(act);v.addWidget(split,1)
        return p
    def _build_advanced(self):
        p=QWidget();v=QVBoxLayout(p);v.setContentsMargins(0,0,0,0);v.setSpacing(10)
        ctl=QHBoxLayout()
        self.edScript=QLineEdit();btnScript=QPushButton("Script");btnScript.clicked.connect(lambda:self._pick(self.edScript,"Choose script","Python (*.py)"))
        self.edConfig=QLineEdit();btnConfig=QPushButton("Config");btnConfig.clicked.connect(lambda:self._pick(self.edConfig,"Choose config","Config (requirements.txt *.yaml *.yml)"))
        self.edEnv=QLineEdit();self.edEnv.setPlaceholderText("env folder (auto if empty)")
        self.cbWatch=QCheckBox("Watch")
        self.cmbProfile=QComboBox();self.cmbProfile.setEditable(True);self.cmbProfile.setPlaceholderText("profile")
        self.edExtra=QLineEdit();self.edExtra.setPlaceholderText("extra args (e.g. -p 8000 --debug)")
        ctl.addWidget(QLabel("Script"));ctl.addWidget(self.edScript,2);ctl.addWidget(btnScript)
        ctl.addWidget(QLabel("Config"));ctl.addWidget(self.edConfig,2);ctl.addWidget(btnConfig)
        ctl.addWidget(QLabel("Env"));ctl.addWidget(self.edEnv);ctl.addWidget(self.cbWatch)
        ctl.addWidget(QLabel("Profile"));ctl.addWidget(self.cmbProfile)
        ctl.addWidget(QLabel("Args"));ctl.addWidget(self.edExtra,2)
        btns=QHBoxLayout()
        self.btnPrepare=QPushButton("Prepare");self.btnPrepare.clicked.connect(self._prepare)
        self.btnRun=QPushButton("Run");self.btnRun.clicked.connect(self._run)
        self.btnBG=QPushButton("Run BG");self.btnBG.clicked.connect(self._run_bg)
        self.btnStop=QPushButton("Stop");self.btnStop.clicked.connect(self._stop);self.btnStop.setEnabled(False)
        self.btnDoctor=QPushButton("Doctor");self.btnDoctor.clicked.connect(self._doctor)
        self.btnList=QPushButton("List Envs");self.btnList.clicked.connect(self._list_envs)
        self.btnValidate=QPushButton("Validate");self.btnValidate.clicked.connect(self._validate_env)
        self.btnFix=QPushButton("Fix Env");self.btnFix.clicked.connect(self._fix_env)
        self.btnReset=QPushButton("Reset Env");self.btnReset.clicked.connect(self._reset_env)
        self.btnShell=QPushButton("Shell");self.btnShell.clicked.connect(self._shell)
        btns.addWidget(self.btnPrepare);btns.addWidget(self.btnRun);btns.addWidget(self.btnBG);btns.addWidget(self.btnStop);btns.addStretch(1)
        btns.addWidget(self.btnDoctor);btns.addWidget(self.btnList);btns.addWidget(self.btnValidate);btns.addWidget(self.btnFix);btns.addWidget(self.btnReset);btns.addWidget(self.btnShell)
        split=QSplitter()
        left=QWidget();lv=QVBoxLayout(left);lv.setContentsMargins(0,0,0,0);lv.setSpacing(8)
        self.tblAdv=QTableWidget(0,5);self.tblAdv.setHorizontalHeaderLabels(["Name","Path","Size(MB)","Deps","Scripts"]);self.tblAdv.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch);self.tblAdv.verticalHeader().setVisible(False);self.tblAdv.setSelectionBehavior(self.tblAdv.SelectionBehavior.SelectRows)
        pk=QHBoxLayout();self.edPkg=QLineEdit();self.edPkg.setPlaceholderText("package name");self.btnAdd=QPushButton("Add");self.btnAdd.clicked.connect(self._add_pkg);self.btnRem=QPushButton("Remove");self.btnRem.clicked.connect(self._rem_pkg)
        lv.addWidget(self.tblAdv);pk.addWidget(QLabel("Package"));pk.addWidget(self.edPkg);pk.addWidget(self.btnAdd);pk.addWidget(self.btnRem);lv.addLayout(pk)
        right=QWidget();rv=QVBoxLayout(right);rv.setContentsMargins(0,0,0,0);rv.setSpacing(8)
        self.consoleAdv=QTextEdit();self.consoleAdv.setReadOnly(True);rv.addWidget(self.consoleAdv,1)
        bbar=QHBoxLayout();self.lblSpinAdv=QLabel("");self.barAdv=QProgressBar();self.barAdv.setFixedHeight(6);self.barAdv.setTextVisible(False);self.spinAdv=Spinner(self.barAdv,self.lblSpinAdv);bbar.addWidget(self.lblSpinAdv);bbar.addWidget(self.barAdv,1);rv.addLayout(bbar)
        split.addWidget(left);split.addWidget(right);split.setStretchFactor(0,1);split.setStretchFactor(1,2)
        v.addLayout(ctl);v.addLayout(btns);v.addWidget(split,1)
        return p
    def _open_config_maker(self):
        seed=None
        p=self.edConfig.text().strip() if hasattr(self,"edConfig") else ""
        if p and Path(p).exists():seed=Path(p).read_text(encoding="utf-8")
        dlg=ConfigMakerDialog(self,seed); 
        if dlg.exec():
            import yaml
            txt=dlg.result_yaml or ""
            if not txt:return
            if p:
                try:Path(p).write_text(txt,encoding="utf-8");QMessageBox.information(self,"Saved",p)
                except Exception as e:QMessageBox.critical(self,"Save failed",str(e));return
            else:
                sp,_=QFileDialog.getSaveFileName(self,"Save YAML",str(Path.cwd()),"YAML (*.yaml *.yml)")
                if not sp:return
                Path(sp).write_text(txt,encoding="utf-8");self.edConfig.setText(sp)
            try:self._init_profiles()
            except Exception:pass
    def _init_profiles(self):
        try:
            self.cmbProfile.clear()
            p=self.edConfig.text().strip()
            if not p or not Path(p).exists():return
            cfg=self.runner.parse_config(p)
            names=list((cfg.get("profiles") or {}).keys())
            if names:self.cmbProfile.addItems(names)
            ap=cfg.get("active_profile")
            if ap and names and ap in names:self.cmbProfile.setCurrentText(ap)
        except Exception:pass
    def _style(self):
        self.setStyleSheet("*{font-family:Inter,Arial,Segoe UI,Roboto,Helvetica,system-ui,sans-serif;font-size:13px} QMainWindow{background:#0f1115;color:#e6e6e6} QLabel{color:#e6e6e6} QLineEdit,QTextEdit,QComboBox{background:#121621;color:#e6e6e6;border:1px solid #2a2f3a;border-radius:8px;padding:8px} QCheckBox{spacing:6px} QPushButton{background:#1b1f2a;color:#e6e6e6;border:1px solid #2a2f3a;border-radius:10px;padding:8px 14px} QPushButton:hover{background:#222736} QProgressBar{background:#171a22;border:1px solid #2a2f3a;border-radius:6px}")
    def _center(self):
        r=self.frameGeometry();c=QApplication.primaryScreen().availableGeometry().center();r.moveCenter(c);self.move(r.topLeft())
    def _toggle_view(self):
        self.advanced=not self.advanced
        self.stack.setCurrentIndex(1 if self.advanced else 0)
        self.btnToggle.setText("Switch to Normal" if self.advanced else "Switch to Advanced")
        self._list_envs()
    def _pick(self,ed:QLineEdit,title,ft):
        f,_=QFileDialog.getOpenFileName(self,title,str(Path.cwd()),ft)
        if f:ed.setText(f)
        if ed is self.edConfig:self._init_profiles()
    def _detect(self,script): 
        try:p=self.runner.smart_auto_detect_config(script);return p or ""
        except:return ""
    def _env_for(self,script,override=""):
        if override:return Path(override)
        return Path(Path(script).stem+"_env")
    def _log(self,s):
        if self.advanced:self.consoleAdv.append(s)
        else:self.console.append(s)
    def _spin(self):return self.spinAdv if self.advanced else self.spin
    def _normal_autodetect(self):
        s=self.nScript.text().strip()
        if not s or not Path(s).exists():self._log("Select a valid script");return
        c=self._detect(s)
        if not c:self._log("No config found; create requirements.txt or YAML");return
        self.nConfig.setText(c);self._log("Config auto-detected")
    def _easy_start(self):
        s=self.nScript.text().strip();c=self.nConfig.text().strip() or self._detect(s)
        if not s or not Path(s).exists():self._log("Select a valid script");return
        if not c or not Path(c).exists():self._log("No config found");return
        cfg=self.runner.parse_config(c);env=self._env_for(s,"")
        self._spin().start("Preparing...")
        def work():
            try:self.runner.create_virtual_environment(env,cfg.get("python_version"));self.runner.install_dependencies(env,cfg);py=self.runner.get_python_path(env);args=[str(py),s];ex=cfg.get("environment_variables",{});return ("ok",(args,os.environ.copy()|ex))
            except Exception as e:return ("err",str(e))
        def done(res):
            if res[0]=="ok":
                self._start_proc(res[1][0],env=res[1][1]);self._spin().stop(True);self.btnNormalStop.setEnabled(True)
            else:self._spin().stop(False);self._log(f"❌ {res[1]}")
            self._list_envs()
        threading.Thread(target=lambda:self._finish_async(work,done),daemon=True).start()
    def _init_profiles(self):
        cp=self.edConfig.text().strip()
        if cp and Path(cp).exists():
            try:
                d=self.runner.parse_config(cp)
                names=list(d.get("profiles",{}).keys())
                self.cmbProfile.clear()
                if names:self.cmbProfile.addItems(names)
            except:pass
    def _prepare(self):
        s=self.edScript.text().strip()
        if not s or not Path(s).exists():self._log("Select a valid script");return
        c=self.edConfig.text().strip() or self._detect(s)
        if not c or not Path(c).exists():self._log("No config found; create requirements.txt or YAML");return
        cfg=self.runner.parse_config(c);p=self.cmbProfile.currentText().strip()
        if p and p in cfg.get("profiles",{}):cfg["active_profile"]=p
        env=self._env_for(s,self.edEnv.text().strip())
        self._spin().start("Preparing environment...")
        def work():
            try:self.runner.create_virtual_environment(env,cfg.get("python_version"));self.runner.install_dependencies(env,cfg);return ("ok",env)
            except Exception as e:return ("err",str(e))
        def done(res):
            self._spin().stop(res[0]=="ok")
            if res[0]=="ok":self._log(f"✅ Prepared: {res[1]}")
            else:self._log(f"❌ {res[1]}")
            self._list_envs()
        threading.Thread(target=lambda:self._finish_async(work,done),daemon=True).start()
    def _run(self):
        s=self.edScript.text().strip()
        if not s or not Path(s).exists():self._log("Select a valid script");return
        c=self.edConfig.text().strip() or self._detect(s)
        if not c or not Path(c).exists():self._log("No config found");return
        cfg=self.runner.parse_config(c);p=self.cmbProfile.currentText().strip()
        if p and p in cfg.get("profiles",{}):cfg["active_profile"]=p
        env=self._env_for(s,self.edEnv.text().strip());self.runner.create_virtual_environment(env,cfg.get("python_version"));self.runner.install_dependencies(env,cfg)
        if self.cbWatch.isChecked():
            py=Path(__file__).with_name("pyrunner.py");args=[sys.executable,str(py),"run",s,"--watch"]; 
            if self.edEnv.text().strip():args+=["--env",self.edEnv.text().strip()]
            if p:args+=["--profile",p]
            ex=self.edExtra.text().strip()
            if ex:args+=ex.split()
            self._start_proc(args)
        else:
            py=self.runner.get_python_path(env);args=[str(py),s];ex=self.edExtra.text().strip()
            if ex:args+=ex.split()
            self._start_proc(args,env=os.environ.copy()|cfg.get("environment_variables",{}))
    def _run_bg(self):
        s=self.edScript.text().strip()
        if not s or not Path(s).exists():self._log("Select a valid script");return
        c=self.edConfig.text().strip() or self._detect(s)
        if not c or not Path(c).exists():self._log("No config found");return
        cfg=self.runner.parse_config(c);p=self.cmbProfile.currentText().strip()
        if p and p in cfg.get("profiles",{}):cfg["active_profile"]=p
        env=self._env_for(s,self.edEnv.text().strip());self.runner.create_virtual_environment(env,cfg.get("python_version"));self.runner.install_dependencies(env,cfg)
        ex=self.edExtra.text().strip().split() if self.edExtra.text().strip() else []
        pid=self.runner.run_script(s,env,extra_args=ex,run_in_background=True,env_vars=cfg.get("environment_variables",{}))
        self._log(f"BG PID: {pid}")
    def _start_proc(self,cmd,env=None):
        if self.proc and self.proc.isRunning():self._log("Process already running");return
        if self.advanced:self.consoleAdv.clear()
        else:self.console.clear()
        self._spin().start("Running...")
        self.proc=ProcThread(cmd,env=env);self.proc.line.connect(lambda l:self._log(l));self.proc.finished.connect(self._proc_done)
        if self.advanced:self.btnStop.setEnabled(True)
        else:self.btnNormalStop.setEnabled(True)
        self.proc.start()
    def _proc_done(self,rc):
        self._spin().stop(rc==0)
        if self.advanced:self.btnStop.setEnabled(False)
        else:self.btnNormalStop.setEnabled(False)
        self._log(f"[exit {rc}]")
    def _stop(self):
        if self.proc and self.proc.isRunning():self.proc.stop();self._log("Stopping...")
    def _env_from_ui(self):
        if self.advanced:
            e=self.edEnv.text().strip()
            if e:return Path(e)
            s=self.edScript.text().strip()
            if s:return self._env_for(s,"")
        else:
            s=self.nScript.text().strip()
            if s:return self._env_for(s,"")
        self._log("Set Env or Script first");return None
    def _doctor(self):
        self._spin().start("Doctor...")
        def work():
            try:return json.dumps(self.runner.doctor_diagnose(),indent=2)
            except Exception as e:return f"ERR: {e}"
        def done(out):self._spin().stop(True);self._log(out)
        threading.Thread(target=lambda:self._finish_async(work,done),daemon=True).start()
    def _list_envs(self):
        def filt(items):
            r=[]
            for info in items:
                name=info.name
                if name==GUI_ENV_NAME:continue
                p=Path(info.path)
                if p.name==GUI_ENV_NAME:continue
                r.append(info)
            return r
        try:
            envs=filt(self.runner.list_environments())
            table=self.tblAdv if self.advanced else self.tbl
            table.setRowCount(0)
            for info in envs:
                r=table.rowCount();table.insertRow(r)
                table.setItem(r,0,QTableWidgetItem(info.name))
                table.setItem(r,1,QTableWidgetItem(info.path))
                table.setItem(r,2,QTableWidgetItem(f"{info.size_mb:.1f}"))
                table.setItem(r,3,QTableWidgetItem(str(info.dependency_count)))
                table.setItem(r,4,QTableWidgetItem(str(len(info.scripts))))
        except Exception as e:self._log(f"List failed: {e}")
    def _validate_env(self):
        env=self._env_from_ui()
        if not env:return
        self._spin().start("Validate...")
        def work():
            try:
                ok,issues=self.runner.validate_environment(env)
                if ok:
                    info=self.runner.get_environment_info(env)
                    return f"VALID\nSize:{info.size_mb:.1f}MB Deps:{info.dependency_count} Scripts:{len(info.scripts)}"
                else:return "INVALID:\n"+"; ".join(issues)
            except Exception as e:return f"ERR:{e}"
        def done(out):self._spin().stop(True);self._log(out)
        threading.Thread(target=lambda:self._finish_async(work,done),daemon=True).start()
    def _fix_env(self):
        env=self._env_from_ui()
        if not env:return
        if env.name==GUI_ENV_NAME or env.parent.name==GUI_ENV_NAME:self._log("Blocked for GUI env");return
        self._spin().start("Fixing...")
        def work():
            try:self.runner.auto_fix_environment(env);return "Fix attempted"
            except Exception as e:return f"ERR:{e}"
        def done(out):self._spin().stop(True);self._log(out)
        threading.Thread(target=lambda:self._finish_async(work,done),daemon=True).start()
    def _reset_env(self):
        env=self._env_from_ui()
        if not env:return
        if env.name==GUI_ENV_NAME or env.parent.name==GUI_ENV_NAME:self._log("Blocked for GUI env");return
        self._spin().start("Resetting...")
        def work():
            try:self.runner.reset_environment(env);return "Reset done"
            except Exception as e:return f"ERR:{e}"
        def done(out):self._spin().stop(True);self._log(out);self._list_envs()
        threading.Thread(target=lambda:self._finish_async(work,done),daemon=True).start()
    def _add_pkg(self):
        env=self._env_from_ui()
        if not env or not self.edPkg.text().strip():return
        if env.name==GUI_ENV_NAME or env.parent.name==GUI_ENV_NAME:self._log("Blocked for GUI env");return
        self._spin().start("Installing package...")
        def work():
            try:self.runner.add_package_to_env(env,self.edPkg.text().strip());return "Installed"
            except Exception as e:return f"ERR:{e}"
        def done(out):self._spin().stop(True);self._log(out);self._validate_env()
        threading.Thread(target=lambda:self._finish_async(work,done),daemon=True).start()
    def _rem_pkg(self):
        env=self._env_from_ui()
        if not env or not self.edPkg.text().strip():return
        if env.name==GUI_ENV_NAME or env.parent.name==GUI_ENV_NAME:self._log("Blocked for GUI env");return
        self._spin().start("Removing package...")
        def work():
            try:self.runner.remove_package_from_env(env,self.edPkg.text().strip());return "Removed"
            except Exception as e:return f"ERR:{e}"
        def done(out):self._spin().stop(True);self._log(out);self._validate_env()
        threading.Thread(target=lambda:self._finish_async(work,done),daemon=True).start()
    def _shell(self):
        env=self._env_from_ui()
        if not env:return
        if env.name==GUI_ENV_NAME or env.parent.name==GUI_ENV_NAME:self._log("Blocked for GUI env");return
        def go():
            try:self.runner.launch_shell(env)
            except Exception as e:self._log(str(e))
        threading.Thread(target=go,daemon=True).start()
    def _finish_async(self,fn,cb):
        r=fn();QTimer.singleShot(0,lambda:cb(r))
def main():
    app=QApplication(sys.argv);w=Main();w.show();return app.exec()
if __name__=="__main__":sys.exit(main())