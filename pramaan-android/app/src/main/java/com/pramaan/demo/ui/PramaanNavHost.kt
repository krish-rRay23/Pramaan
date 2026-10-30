package com.pramaan.demo.ui

import androidx.compose.runtime.Composable
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.pramaan.demo.PramaanViewModel

import androidx.compose.runtime.LaunchedEffect

@Composable
fun PramaanNavHost(
    viewModel: PramaanViewModel = viewModel(),
    navController: NavHostController = rememberNavController()
) {
    LaunchedEffect(viewModel.pendingNavigation) {
        viewModel.pendingNavigation?.let { dest ->
            navController.navigate(dest) {
                launchSingleTop = true
            }
            viewModel.clearPendingNavigation()
        }
    }

    NavHost(navController = navController, startDestination = "home") {
        composable("home") {
            HomeScreen(navController, viewModel)
        }
        composable("handoff") {
            TrustedHandoffScreen(navController, viewModel)
        }
        composable("details") {
            InteractionDetailsScreen(navController, viewModel)
        }
        composable("action_gate") {
            ExactActionGateScreen(navController, viewModel)
        }
        composable("kill_switch_report") {
            KillSwitchReportScreen(navController, viewModel)
        }
        composable("blocked") {
            BlockedInteractionScreen(navController, viewModel)
        }
        composable("receipt") {
            TrustReceiptScreen(navController, viewModel)
        }
        composable("history") {
            TrustHistoryScreen(navController, viewModel)
        }
        composable("kyc") {
            KycScreen(navController, viewModel)
        }
    }
}
