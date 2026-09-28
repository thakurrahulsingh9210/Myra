package com.myra.assistant

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.auth0.android.Auth0
import com.auth0.android.provider.WebAuthProvider

class MainActivity : ComponentActivity() {
    private lateinit var account: Auth0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        account = Auth0(this)
        setContent {
            MaterialTheme {
                MyraScreen(onLogin = {
                    WebAuthProvider.login(account)
                        .start(this, object : com.auth0.android.callback.Callback<com.auth0.android.result.Credentials, com.auth0.android.authentication.AuthenticationException> {
                            override fun onSuccess(result: com.auth0.android.result.Credentials) { }
                            override fun onFailure(error: com.auth0.android.authentication.AuthenticationException) { }
                        })
                })
            }
        }
    }
}

@Composable
private fun MyraScreen(onLogin: () -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize().padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("Myra", style = MaterialTheme.typography.displayMedium)
        Text("Your native Android voice assistant", modifier = Modifier.padding(top = 8.dp, bottom = 24.dp))
        Button(onClick = onLogin) { Text("Sign in with Auth0") }
    }
}
