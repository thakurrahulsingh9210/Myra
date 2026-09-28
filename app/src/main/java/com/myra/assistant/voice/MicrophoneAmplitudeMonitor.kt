package com.myra.assistant.voice

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import androidx.core.content.ContextCompat
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlin.math.sqrt

class MicrophoneAmplitudeMonitor(private val context: Context) {
    private val _amplitude = MutableStateFlow(0f)
    val amplitude: StateFlow<Float> = _amplitude.asStateFlow()

    private var recordJob: Job? = null
    private var recorder: AudioRecord? = null

    fun start(scope: CoroutineScope) {
        if (recordJob?.isActive == true) return
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            return
        }

        val sampleRate = 16_000
        val minBuffer = AudioRecord.getMinBufferSize(
            sampleRate,
            AudioFormat.CHANNEL_IN_MONO,
            AudioFormat.ENCODING_PCM_16BIT
        )
        if (minBuffer <= 0) return

        val buffer = ShortArray((minBuffer / 2).coerceAtLeast(1024))
        val audioRecord = AudioRecord(
            MediaRecorder.AudioSource.VOICE_RECOGNITION,
            sampleRate,
            AudioFormat.CHANNEL_IN_MONO,
            AudioFormat.ENCODING_PCM_16BIT,
            buffer.size * 2
        )

        recorder = audioRecord
        audioRecord.startRecording()

        recordJob = scope.launch(Dispatchers.Default) {
            try {
                while (isActive) {
                    val count = audioRecord.read(buffer, 0, buffer.size)
                    if (count > 0) {
                        var sumSquares = 0.0
                        for (i in 0 until count) {
                            val normalized = buffer[i] / 32768.0
                            sumSquares += normalized * normalized
                        }
                        val rms = sqrt(sumSquares / count).toFloat()
                        _amplitude.value = (rms * 4f).coerceIn(0f, 1f)
                    }
                }
            } finally {
                runCatching { audioRecord.stop() }
                audioRecord.release()
                recorder = null
                _amplitude.value = 0f
            }
        }
    }

    fun stop() {
        recordJob?.cancel()
        recordJob = null
    }
}
