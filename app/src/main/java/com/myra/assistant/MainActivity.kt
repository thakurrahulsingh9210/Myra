package com.myra.assistant

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
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
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.auth0.android.Auth0
import com.auth0.android.provider.WebAuthProvider
import com.myra.assistant.voice.MicrophoneAmplitudeMonitor
import com.myra.assistant.voice.VoiceState
import kotlin.math.PI
import kotlin.math.sin
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    private lateinit var account: Auth0
    private lateinit var microphone: MicrophoneAmplitudeMonitor

    private var amplitude by mutableFloatStateOf(0f)
    private var voiceState by mutableStateOf(VoiceState.IDLE)

    private val permissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
            if (granted) microphone.start(lifecycleScope)
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        account = Auth0(this)
        microphone = MicrophoneAmplitudeMonitor(this)

        lifecycleScope.launch {
            microphone.amplitude.collectLatest { amplitude = it }
        }

        setContent {
            MaterialTheme {
                MyraScreen(
                    refreshRateHz = display.refreshRate,
                    amplitude = amplitude,
                    voiceState = voiceState,
                    onStartListening = ::startMicrophone,
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

    override fun onDestroy() {
        microphone.stop()
        super.onDestroy()
    }

    private fun startMicrophone() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) ==
            PackageManager.PERMISSION_GRANTED
        ) {
            microphone.start(lifecycleScope)
            voiceState = VoiceState.LISTENING
        } else {
            permissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
        }
    }
}

@Composable
private fun MyraScreen(
    refreshRateHz: Float,
    amplitude: Float,
    voiceState: VoiceState,
    onStartListening: () -> Unit,
    onLogin: () -> Unit
) {
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
            targetFps = targetFps,
            amplitude = amplitude,
            voiceState = voiceState
        )

        Text("Myra", style = MaterialTheme.typography.displayMedium)
        Text(
            text = voiceState.name.lowercase().replaceFirstChar { it.uppercase() },
            modifier = Modifier.padding(top = 8.dp, bottom = 24.dp)
        )

        Button(onClick = onStartListening) {
            Text("Talk to Myra")
        }

        Button(onClick = onLogin, modifier = Modifier.padding(top = 12.dp)) {
            Text("Sign in with Auth0")
        }
    }
}

@Composable
private fun MyraOrb(
    modifier: Modifier = Modifier,
    targetFps: Int,
    amplitude: Float,
    voiceState: VoiceState
) {
    var phase by remember { mutableFloatStateOf(0f) }
    var smoothedAmplitude by remember { mutableFloatStateOf(0f) }

    LaunchedEffect(targetFps, voiceState) {
        var previousFrameNanos = 0L
        val frameIntervalNanos = 1_000_000_000L / targetFps

        while (true) {
            withInfiniteAnimationFrameNanos { frameTimeNanos ->
                if (previousFrameNanos == 0L ||
                    frameTimeNanos - previousFrameNanos >= frameIntervalNanos
                ) {
                    previousFrameNanos = frameTimeNanos
                    phase = ((frameTimeNanos % 2_000_000_000L).toFloat() / 2_000_000_000f) *
                        (2f * PI.toFloat())

                    val target = when (voiceState) {
                        VoiceState.LISTENING -> amplitude
                        VoiceState.SPEAKING -> 0.55f + amplitude * 0.45f
                        VoiceState.THINKING -> 0.35f
                        VoiceState.CONNECTING -> 0.18f
                        VoiceState.ERROR -> 0.08f
                        VoiceState.IDLE -> 0f
                    }
                    smoothedAmplitude += (target - smoothedAmplitude) * 0.16f
                }
            }
        }
    }

    Canvas(modifier = modifier) {
        val radius = size.minDimension * 0.28f
        val stateBoost = when (voiceState) {
            VoiceState.SPEAKING -> 1.18f
            VoiceState.THINKING -> 1.08f
            VoiceState.CONNECTING -> 1.04f
            else -> 1f
        }
        val pulse = stateBoost + smoothedAmplitude * 0.22f + 0.04f * sin(phase)

        drawCircle(
            radius = radius * pulse,
            center = center,
            style = Stroke(width = 5.dp.toPx())
        )
    }
}
