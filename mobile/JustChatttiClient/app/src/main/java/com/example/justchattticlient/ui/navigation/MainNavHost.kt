package com.example.justchattticlient.ui.navigation

import androidx.navigation.NavController
import androidx.navigation.NavGraphBuilder
import androidx.navigation.compose.composable
import androidx.navigation.navigation
import feature.login.api.LoginRoute
import feature.login.impl.LoginScreen
import feature.register.api.RegisterRoute
import feature.register.impl.RegisterScreen

fun NavGraphBuilder.addAuthGraph(
    navController: NavController
) {
    navigation<AuthGraph>(
        startDestination = LoginRoute
    ) {
        composable<RegisterRoute> {
            RegisterScreen(
                navigateToLogin = { navController.navigate(LoginRoute) }
            )
        }

        composable<LoginRoute> {
            LoginScreen(
                onSuccessLogin = {},
                navigateToRegister = { navController.navigate(RegisterRoute) },
                navigateToForgotPassword = {}
            )
        }
    }
}