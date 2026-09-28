package com.myra.assistant.actions

import android.content.Context
import android.content.Intent
import android.net.Uri

class AndroidActionEngine(private val context: Context) : ActionEngine {

    override suspend fun execute(action: DeviceAction): ActionResult {
        return runCatching {
            when (action) {
                is DeviceAction.OpenApp -> openApp(action.packageName)
                is DeviceAction.OpenUrl -> openUrl(action.url)
                is DeviceAction.MakeCall -> ActionResult.NeedsConfirmation(
                    "Call ${action.contactName}?"
                )
                is DeviceAction.SendSms -> ActionResult.NeedsConfirmation(
                    "Send this SMS to ${action.contactName}: ${action.message}"
                )
                is DeviceAction.SetAlarm -> ActionResult.Failure(
                    "Alarm execution is not connected yet."
                )
                is DeviceAction.CreateReminder -> ActionResult.Failure(
                    "Reminder execution is not connected yet."
                )
                is DeviceAction.ControlMedia -> ActionResult.Failure(
                    "Media control is not connected yet."
                )
            }
        }.getOrElse {
            ActionResult.Failure(it.message ?: "Unable to execute action.")
        }
    }

    private fun openApp(packageName: String): ActionResult {
        val intent = context.packageManager.getLaunchIntentForPackage(packageName)
            ?: return ActionResult.Failure("App is not installed: $packageName")

        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        context.startActivity(intent)
        return ActionResult.Success("Opened $packageName")
    }

    private fun openUrl(url: String): ActionResult {
        val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url)).apply {
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        }
        if (intent.resolveActivity(context.packageManager) == null) {
            return ActionResult.Failure("No app can open that link.")
        }
        context.startActivity(intent)
        return ActionResult.Success("Opened link")
    }
}
