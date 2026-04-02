package com.example.justchattticlient.ui

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.rememberNavController
import com.example.justchattticlient.ui.navigation.AuthGraph
import com.example.justchattticlient.ui.navigation.addAuthGraph
import feature.register.impl.RegisterScreen
import uikit.theme.JustChatttiClientTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            val navController = rememberNavController()

            JustChatttiClientTheme {
                Scaffold(
                    contentWindowInsets = WindowInsets(0),
                    modifier = Modifier.fillMaxSize(),
                ) { innerPadding ->
                    NavHost(
                        navController = navController,
                        startDestination = AuthGraph,
                        modifier = Modifier.padding(innerPadding)
                    ) {
                        addAuthGraph(navController)
                    }
                }
            }
        }
    }
}