package com.myra.assistant

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.animation.core.withInfiniteAnimationFrameNanos
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.unit.dp
import com.auth0.android.Auth0
import com.auth0.android.provider.WebAuthProvider
import kotlin.math.PI
import kotlin.math.sin

class MainActivity : ComponentActivity() {
    private lateinit var account: Auth0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        account = Auth0(this)

        setContent {
            MaterialTheme {
                MyraScreen(
                    refreshRateHz = display.refreshRate,
                    onLogin = {
                        WebAuthProvider.login(account)
                            .start(this, object : com.auth0.android.callback.Callback<com.auth0.android.result.Credentials, com.auth0.android.authentication.AuthenticationException> {
                                override fun onSuccess(result: com.auth0.android.result.Credentials) = Unit
                                override fun onFailure(error: com.auth0.android.authentication.AuthenticationException) = Unit
                            })
                    }
                )
            }
        }
    }
}

@Composable
private fun MyraScreen(refreshRateHz: Float, onLogin: () -> Unit) {
    val targetFps = remember(refreshRateHz) {
        if (refreshRateHz >= 110f) 120 else 60
    }

    Column(
        modifier = Modifier.fillMaxSize().padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        MyraOrb(
            modifier = Modifier.padding(bottom = 24.dp),
            targetFps = targetFps
        )
        Text("Myra", style = MaterialTheme.typography.displayMedium)
        Text(
            text = "Adaptive ${targetFps} FPS UI",
            modifier = Modifier.padding(top = 8.dp, bottom = 24.dp)
        )
        Button(onClick = onLogin) {
            Text("Sign in with Auth0")
        }
    }
}

@Composable
private fun MyraOrb(modifier: Modifier = Modifier, targetFps: Int) {
    var phase by remember { mutableFloatStateOf(0f) }

    LaunchedEffect(targetFps) {
        var previousFrameNanos = 0L
        val frameIntervalNanos = 1_000_000_000L / targetFps

        while (true) {
            withInfiniteAnimationFrameNanos { frameTimeNanos ->
                if (previousFrameNanos == 0L || frameTimeNanos - previousFrameNanos >= frameIntervalNanos) {
                    previousFrameNanos = frameTimeNanos
                    phase = ((frameTimeNanos % 2_000_000_000L).toFloat() / 2_000_000_000f) * (2f * PI.toFloat())
                }
            }
        }
    }

    Canvas(modifier = modifier) {
        val radius = size.minDimension * 0.28f
        val pulse = 1f + 0.08f * sin(phase)
        drawCircle(
            radius = radius * pulse,
            center = center,
            style = Stroke(width = 5.dp.toPx())
        )
    }
}
