package com.example.justchattticlient.ui

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.navigation.compose.rememberNavController
import feature.register.impl.RegisterScreen
import uikit.theme.JustChatttiClientTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            JustChatttiClientTheme {
                val navController = rememberNavController()
                RegisterScreen(
                    navigateToLogin = {

                    }
                )
            }
        }
    }
}