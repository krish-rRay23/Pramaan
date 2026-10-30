package com.pramaan.demo.ui

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Dangerous
import androidx.compose.material.icons.filled.GppBad
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import com.pramaan.demo.PramaanViewModel
import com.pramaan.demo.ui.theme.AlertRed
import com.pramaan.demo.ui.theme.CanvasLightBg
import com.pramaan.demo.ui.theme.CanvasWhite
import com.pramaan.demo.ui.theme.GlassBorderLight
import com.pramaan.demo.ui.theme.TextMuted
import com.pramaan.demo.ui.theme.TextPrimary
import com.pramaan.demo.ui.theme.TextWhite
import com.pramaan.demo.ui.theme.TvsGreen
import com.pramaan.demo.ui.theme.TvsGreenDark
import com.pramaan.demo.ui.theme.TvsNavy

@Composable
fun BlockedInteractionScreen(
    navController: NavHostController,
    viewModel: PramaanViewModel = viewModel(),
) {
    val context = LocalContext.current
    val verifyRes = viewModel.lastVerifyResponse
    val receipt = viewModel.lastReceipt

    // Minimalist Light Canvas with subtle top alert wash
    val backgroundBrush = Brush.verticalGradient(
        colors = listOf(
            Color(0xFFFFF1F2),
            Color(0xFFFAFAFA),
            CanvasWhite
        )
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(backgroundBrush)
            .statusBarsPadding()
            .verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        // High Impact Red Warning Header (Glassmorphic White)
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp)
                .clip(RoundedCornerShape(24.dp))
                .background(Color.White)
                .border(1.dp, Color(0xFFFCA5A5), RoundedCornerShape(24.dp))
                .padding(28.dp),
            contentAlignment = Alignment.Center
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Box(
                    modifier = Modifier
                        .size(80.dp)
                        .clip(CircleShape)
                        .background(Color(0xFFFEE2E2))
                        .border(1.5.dp, AlertRed, CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        Icons.Filled.GppBad,
                        contentDescription = null,
                        tint = AlertRed,
                        modifier = Modifier.size(50.dp)
                    )
                }
                Spacer(Modifier.height(16.dp))
                Text(
                    text = "ACTION BLOCKED & UNVERIFIED",
                    color = TvsNavy,
                    fontWeight = FontWeight.ExtraBold,
                    fontSize = 18.sp,
                    letterSpacing = 0.8.sp
                )
                Spacer(Modifier.height(4.dp))
                Text(
                    text = "DO NOT TRANSFER MONEY OR SHARE OTP",
                    color = AlertRed,
                    fontWeight = FontWeight.Bold,
                    fontSize = 12.sp,
                    letterSpacing = 0.5.sp
                )
            }
        }

        Column(
            modifier = Modifier.padding(horizontal = 20.dp, vertical = 4.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Security Violation Breakdown (GlassCard White)
            GlassCard(
                borderColor = Color(0xFFFECACA),
                glowColor = Color(0x40EF4444)
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Filled.Dangerous, contentDescription = null, tint = AlertRed, modifier = Modifier.size(24.dp))
                    Spacer(Modifier.width(10.dp))
                    Text(
                        "Pramaan Policy Violation",
                        color = AlertRed,
                        fontWeight = FontWeight.ExtraBold,
                        fontSize = 14.sp
                    )
                }
                Spacer(Modifier.height(12.dp))
                Text(
                    text = verifyRes?.reason ?: "Unable to verify. Do not proceed.",
                    color = TvsNavy,
                    fontWeight = FontWeight.SemiBold,
                    fontSize = 13.sp,
                    lineHeight = 18.sp
                )
            }

            // TVS Master Authorization Comparison (GlassCard White)
            GlassCard {
                Text(
                    "RECORDED TVS AUTHORITY VS CLAIM",
                    color = TextMuted,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 1.sp
                )
                Spacer(Modifier.height(12.dp))
                LabelValueRow("Policy Decision", verifyRes?.decision ?: "BLOCKED", valueColor = AlertRed)
                if (!verifyRes?.reasonCode.isNullOrBlank()) {
                    LabelValueRow("Reason Code", verifyRes?.reasonCode ?: "POL_DESTINATION_MISMATCH", isMono = true)
                }
                LabelValueRow("Policy Version", verifyRes?.policyVersion ?: "3.2.0")
                LabelValueRow("Signature Valid", if (verifyRes?.signatureValid == true) "YES" else "FORGED / TAMPERED", valueColor = if (verifyRes?.signatureValid == true) TvsGreenDark else AlertRed)
                LabelValueRow("Freshness", if (verifyRes?.fresh == true) "FRESH" else "EXPIRED", valueColor = if (verifyRes?.fresh == true) TvsGreenDark else AlertRed)
                LabelValueRow("Agent Authorized", if (verifyRes?.agentAuthorized == true) "YES" else "UNAUTHORIZED / FAKE", valueColor = if (verifyRes?.agentAuthorized == true) TvsGreenDark else AlertRed)
                LabelValueRow("Destination Match", if (verifyRes?.destinationVerified == true) "MATCHED" else "UNAUTHORIZED VPA", valueColor = if (verifyRes?.destinationVerified == true) TvsGreenDark else AlertRed)
            }

            // Trust Receipt Reference
            if (receipt != null) {
                GlassCard {
                    Text("AUDIT PROOF GENERATED", color = TextMuted, fontSize = 11.sp, fontWeight = FontWeight.Bold, letterSpacing = 1.sp)
                    Spacer(Modifier.height(10.dp))
                    LabelValueRow("Audit Receipt ID", receipt.receiptId, isMono = true)
                    LabelValueRow("TVS Auth Ref", receipt.authorizationRef, isMono = true)
                    Spacer(Modifier.height(4.dp))
                    Text(
                        "This blocked attempt has been permanently logged in TVS Credit's Audit Trail.",
                        color = TextMuted,
                        fontSize = 11.sp,
                    )
                }
            }

            Spacer(Modifier.height(4.dp))

            DangerButton(
                text = "Call TVS Fraud Helpline (1800-102-2221)",
                onClick = {
                    try {
                        val dialIntent = Intent(Intent.ACTION_DIAL).apply {
                            data = Uri.parse("tel:18001022221")
                        }
                        context.startActivity(dialIntent)
                    } catch (_: Exception) {
                    }
                }
            )

            SecondaryButton(
                text = "Return to Safe Dashboard",
                onClick = {
                    navController.navigate("home") {
                        popUpTo("home") { inclusive = true }
                    }
                }
            )

            Spacer(Modifier.height(16.dp))
        }
    }
}
