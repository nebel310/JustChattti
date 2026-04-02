package com.example.justchattticlient.ui.navigation

import core.navigation.BaseRoute
import kotlinx.serialization.Serializable

@Serializable
data object AuthGraph: BaseRoute

@Serializable
data object ChatsGraph: BaseRoute

@Serializable
data object SettingsGraph: BaseRoute

@Serializable
data object AccountGraph: BaseRoute