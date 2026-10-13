"""Build Pixel Wheels 1.0.1 Java source as an embedded, isolated activity."""
from pathlib import Path
import os
import shutil
import subprocess
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'.sources/pixelwheels'
if subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()!='de6a692f3b6f2ade9e914982e0aeadb4aa2b1de3':
    raise SystemExit('Pixel Wheels must be pinned to 1.0.1.')
module=ROOT/'build/pixel-embedded';module.mkdir(parents=True,exist_ok=True)
engine=ROOT/'.sources/retroarch/pkg/android/phoenix'
for name in ('gradlew','gradlew.bat'):shutil.copy2(engine/name,module/name)
shutil.copytree(engine/'gradle',module/'gradle',dirs_exist_ok=True)
java=module/'java';java.mkdir(exist_ok=True)
for tree in ('core/src','android/src/main','android/src/itchio'):
    shutil.copytree(source/tree,java,dirs_exist_ok=True)
for p in java.rglob('*.java'):
    p.write_text(p.read_text().replace('com.agateau.pixelwheels.android','io.precisiondata.joyorbit.wheels'))
version=java/'com/agateau/pixelwheels/VersionInfo.java';version.parent.mkdir(parents=True,exist_ok=True)
version.write_text('package com.agateau.pixelwheels; public class VersionInfo { public static final String VERSION="1.0.1"; }\n')
activity=java/'com/agateau/pixelwheels/android/AndroidLauncher.java'
text=activity.read_text().replace('public class AndroidLauncher extends AndroidApplication {','''public class AndroidLauncher extends AndroidApplication {
    private boolean joySelectDown;
    private boolean joyStartDown;
    @Override
    public boolean dispatchKeyEvent(android.view.KeyEvent event) {
        if (event.getKeyCode() == android.view.KeyEvent.KEYCODE_BUTTON_SELECT)
            joySelectDown = event.getAction() == android.view.KeyEvent.ACTION_DOWN;
        if (event.getKeyCode() == android.view.KeyEvent.KEYCODE_BUTTON_START)
            joyStartDown = event.getAction() == android.view.KeyEvent.ACTION_DOWN;
        if (joySelectDown && joyStartDown && event.getAction() == android.view.KeyEvent.ACTION_DOWN) {
            Gdx.app.postRunnable(() -> Gdx.app.exit());
            return true;
        }
        if (event.getKeyCode() == android.view.KeyEvent.KEYCODE_BACK &&
            event.getAction() == android.view.KeyEvent.ACTION_DOWN && event.isLongPress()) {
            Gdx.app.postRunnable(() -> Gdx.app.exit());
            return true;
        }
        return super.dispatchKeyEvent(event);
    }
''',1)
activity.write_text(text)
text=text.replace('super.onWindowFocusChanged(hasFocus);',
    'if (!hasFocus) { joySelectDown = false; joyStartDown = false; }\n        super.onWindowFocusChanged(hasFocus);')
activity.write_text(text)
(module/'AndroidManifest.xml').write_text('''<manifest xmlns:android="http://schemas.android.com/apk/res/android"><application>
<activity android:name="io.precisiondata.joyorbit.wheels.AndroidLauncher" android:exported="true" android:process=":wheels" android:launchMode="singleInstance" android:enableOnBackInvokedCallback="false" android:screenOrientation="landscape" android:configChanges="keyboard|keyboardHidden|navigation|orientation|screenSize" android:theme="@style/GdxTheme"/>
</application></manifest>''')
(module/'local.properties').write_text('sdk.dir='+os.environ['ANDROID_SDK_ROOT']+'\n')
(module/'gradle.properties').write_text('android.useAndroidX=true\norg.gradle.jvmargs=-Xmx4g\n')
(module/'build.gradle').write_text('''buildscript { repositories { google(); mavenCentral() }; dependencies { classpath 'com.android.tools.build:gradle:9.1.0' } }
repositories { google(); mavenCentral() }
apply plugin: 'com.android.library'
configurations { natives }
dependencies {
 implementation 'com.badlogicgames.gdx:gdx:1.9.14'
 implementation 'com.badlogicgames.gdx:gdx-backend-android:1.9.14'
 implementation 'com.badlogicgames.gdx:gdx-box2d:1.9.14'
 implementation 'com.badlogicgames.gdx:gdx-freetype:1.9.14'
 implementation 'com.badlogicgames.gdx-controllers:gdx-controllers-core:2.2.2'
 implementation 'com.badlogicgames.gdx-controllers:gdx-controllers-android:2.2.2'
 implementation 'com.google.code.gson:gson:2.8.5'
 implementation 'androidx.core:core:1.13.1'
 natives 'com.badlogicgames.gdx:gdx-platform:1.9.14:natives-arm64-v8a'
 natives 'com.badlogicgames.gdx:gdx-box2d-platform:1.9.14:natives-arm64-v8a'
 natives 'com.badlogicgames.gdx:gdx-freetype-platform:1.9.14:natives-arm64-v8a'
}
android {
 namespace "io.precisiondata.joyorbit.wheels"
 compileSdkVersion 36
 defaultConfig { minSdkVersion 23 }
 sourceSets { main {
 manifest.srcFile 'AndroidManifest.xml'
 java.srcDirs = ['''+repr(str(java))+''']
 res.srcDirs = ['''+repr(str(source/'android/res'))+''']
 assets.srcDirs = ['''+repr(str(source/'android/assets'))+''']
 jniLibs.srcDirs = ['libs']
 } }
}
tasks.register('copyNatives') {
 doLast {
 configurations.natives.files.each { archive -> copy { from zipTree(archive); include '*.so'; into 'libs/arm64-v8a' } }
 }
}
tasks.named('preBuild').configure { dependsOn 'copyNatives' }
''')
subprocess.run(['sh',str(module/'gradlew'),'-p',str(module),'assembleDebug','--no-daemon'],check=True)
output=ROOT/'build/android-apk/libs';output.mkdir(parents=True,exist_ok=True)
shutil.copy2(module/'build/outputs/aar/pixel-embedded-debug.aar',output/'joyorbit-wheels.aar')
print('Pixel Wheels AAR staged; rebuild APK with runtime dependencies.')
