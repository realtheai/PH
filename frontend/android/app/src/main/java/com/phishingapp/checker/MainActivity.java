package com.phishingapp.checker;

import android.content.Intent;
import android.os.Bundle;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // Share Intent 처리
        handleSendIntent(getIntent());
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        
        // 새로운 Intent 처리 (앱이 이미 실행 중일 때)
        handleSendIntent(intent);
    }

    private void handleSendIntent(Intent intent) {
        String action = intent.getAction();
        String type = intent.getType();

        if (Intent.ACTION_SEND.equals(action) && type != null) {
            if ("text/plain".equals(type)) {
                String sharedText = intent.getStringExtra(Intent.EXTRA_TEXT);
                if (sharedText != null) {
                    // JavaScript로 공유된 텍스트 전달
                    String js = String.format(
                        "localStorage.setItem('sharedMessage', %s); " +
                        "if (window.location.pathname !== '/') { window.location.href = '/'; }",
                        android.text.TextUtils.htmlEncode(sharedText).replace("'", "\\'")
                    );
                    
                    // WebView가 로드된 후 실행
                    getBridge().getWebView().post(() -> {
                        getBridge().getWebView().evaluateJavascript(js, null);
                    });
                }
            }
        }
    }
}
