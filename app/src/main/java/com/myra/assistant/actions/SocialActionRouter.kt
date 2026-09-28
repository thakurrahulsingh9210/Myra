package com.myra.assistant.actions

object SocialActionRouter {

    fun open(service: String, target: String? = null): DeviceAction.OpenUrl? {
        val normalized = service.trim().lowercase()
        val url = when (normalized) {
            "instagram", "insta" ->
                target?.let { "https://www.instagram.com/${it.removePrefix("@")}/" }
                    ?: "https://www.instagram.com/"

            "facebook", "fb" ->
                target?.let { "https://www.facebook.com/${it.removePrefix("@")}" }
                    ?: "https://www.facebook.com/"

            "github", "git hub" ->
                target?.let { "https://github.com/${it.removePrefix("@")}" }
                    ?: "https://github.com/"

            "telegram" ->
                target?.let { "https://t.me/${it.removePrefix("@")}" }
                    ?: "https://telegram.org/"

            else -> return null
        }

        return DeviceAction.OpenUrl(url)
    }
}
