package com.myra.assistant.voice

import kotlinx.coroutines.flow.StateFlow

/** Provider-independent boundary for Myra realtime speech. */
interface RealtimeVoiceEngine {
    val state: StateFlow<VoiceState>
    suspend fun connect()
    suspend fun disconnect()
    fun interrupt()
}
