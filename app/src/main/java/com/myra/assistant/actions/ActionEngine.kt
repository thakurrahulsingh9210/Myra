package com.myra.assistant.actions

interface ActionEngine {
    suspend fun execute(action: DeviceAction): ActionResult
}

sealed interface DeviceAction {
    data class OpenApp(val packageName: String) : DeviceAction
    data class MakeCall(val contactName: String) : DeviceAction
    data class SendSms(val contactName: String, val message: String) : DeviceAction
    data class SetAlarm(val epochMillis: Long) : DeviceAction
    data class CreateReminder(val text: String, val epochMillis: Long?) : DeviceAction
    data class ControlMedia(val command: String) : DeviceAction
}

sealed interface ActionResult {
    data class Success(val message: String) : ActionResult
    data class NeedsConfirmation(val prompt: String) : ActionResult
    data class Failure(val message: String) : ActionResult
}
