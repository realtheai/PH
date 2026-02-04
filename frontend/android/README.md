# 피싱체커 Android 앱

Capacitor 기반 Android 네이티브 앱입니다.

## 📱 APK 정보

- **파일명**: app-debug.apk
- **크기**: 4.4MB
- **위치**: `app/build/outputs/apk/debug/app-debug.apk`
- **타입**: Debug APK (개발용)

## 🚀 빌드 방법

### Debug APK 빌드

```bash
# 1. Next.js 프론트엔드 빌드
cd ..
npm run build

# 2. Capacitor 동기화
npx cap sync android

# 3. APK 빌드
cd android
./gradlew assembleDebug
```

### Release APK 빌드 (서명 필요)

```bash
# 1. 키스토어 생성 (최초 1회)
keytool -genkey -v -keystore phishing-checker.keystore \
  -alias phishing-checker \
  -keyalg RSA -keysize 2048 -validity 10000

# 2. build.gradle에 signing 설정 추가

# 3. Release 빌드
./gradlew assembleRelease
```

## 📦 APK 설치

### ADB를 통한 설치

```bash
adb install app/build/outputs/apk/debug/app-debug.apk
```

### 수동 설치

1. APK 파일을 Android 기기로 전송
2. 파일 관리자에서 APK 클릭
3. "출처를 알 수 없는 앱" 설치 허용
4. 설치 진행

## 🎨 주요 기능

### Share Intent

다른 앱(메시지, 카카오톡 등)에서 "공유" 버튼을 통해 피싱체커로 텍스트 전달

**구현 위치**:
- `app/src/main/AndroidManifest.xml` - Intent Filter 설정
- `app/src/main/java/.../MainActivity.java` - Intent 처리 로직

**동작 방식**:
1. 사용자가 다른 앱에서 텍스트 선택 후 "공유" 클릭
2. 피싱체커 선택
3. MainActivity에서 공유된 텍스트 수신
4. JavaScript로 WebView에 전달
5. 프론트엔드에서 자동으로 분석 시작

## 🛠️ 개발 도구

### Android Studio로 열기

```bash
npx cap open android
```

### 로그 확인

```bash
# 앱 로그 보기
adb logcat | grep PhishingChecker

# 전체 로그
adb logcat
```

### 디바이스 연결 확인

```bash
adb devices
```

## 📝 설정 파일

### capacitor.config.ts

```typescript
{
  appId: 'com.phishingapp.checker',
  appName: '피싱체커',
  webDir: 'out',
  server: {
    androidScheme: 'https',
    cleartext: true
  }
}
```

### AndroidManifest.xml 주요 설정

- **INTERNET 권한**: 백엔드 API 통신
- **Share Intent**: 텍스트 공유 수신

## 🐛 문제 해결

### 빌드 실패

```bash
# Gradle 캐시 삭제
./gradlew clean

# Gradle Wrapper 재다운로드
./gradlew wrapper --gradle-version 8.14.3
```

### APK 설치 실패

- "출처를 알 수 없는 앱" 설치 허용 확인
- 기존 앱 삭제 후 재설치
- Android 버전 확인 (최소 버전: Android 5.0+)

### Share Intent 작동 안 함

- AndroidManifest.xml의 intent-filter 확인
- MainActivity.java의 handleSendIntent 로직 확인
- 앱 재설치 후 테스트

## 📄 라이선스

MIT License
