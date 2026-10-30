package com.pramaan.demo

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.navigation.compose.rememberNavControllerĪ
import com.pramaan.demo.ui.PramaanNavHost
import com.pramaan.demo.ui.theme.PramaanTheme

class MainActivity : ComponentActivity() {
    private val viewModel: PramaanViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handleIncomingIntent(intent)

        setContent {
            PramaanTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    val navController = rememberNavController()
                    PramaanNavHost(viewModel = viewModel, navController = navController)
                }
            }
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        handleIncomingIntent(intent)
    }

    private fun handleIncomingIntent(intent: Intent?) {
        val data: Uri? = intent?.data
        if (data != null) {
            val token = data.getQueryParameter("token")
            val channel = data.getQueryParameter("channel") ?: "whatsapp"
            if (!token.isNullOrBlank()) {
                viewModel.setChannelOrigin(channel)
                viewModel.handleDeepLinkToken(token)
            }
        }
    }
}
