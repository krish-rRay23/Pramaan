package com.pramaan.demo.ui

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
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.GppBad
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import com.pramaan.demo.PramaanViewModel
import com.pramaan.demo.ui.theme.AlertRed
import com.pramaan.demo.ui.theme.CanvasGlowMid
import com.pramaan.demo.ui.theme.CanvasGlowTop
import com.pramaan.demo.ui.theme.CanvasLightBg
import com.pramaan.demo.ui.theme.CanvasWhite
import com.pramaan.demo.ui.theme.GlassBorderLight
import com.pramaan.demo.ui.theme.TextMint
import com.pramaan.demo.ui.theme.TextMuted
import com.pramaan.demo.ui.theme.TextPrimary
import com.pramaan.demo.ui.theme.TvsGreen
import com.pramaan.demo.ui.theme.TvsGreenDark
import com.pramaan.demo.ui.theme.TvsNavy

@Composable
fun TrustHistoryScreen(
    navController: NavHostController,
    viewModel: PramaanViewModel = viewModel(),
) {
    LaunchedEffect(Unit) {
        viewModel.loadReceiptHistory()
    }

    val history = viewModel.receiptsHistory

    // TVS Credit E.P.I.C 6 Minimalist White Canvas
    val backgroundBrush = Brush.verticalGradient(
        colors = listOf(
            CanvasGlowTop,
            CanvasGlowMid,
            CanvasLightBg,
            CanvasWhite
        )
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(backgroundBrush)
            .statusBarsPadding(),
    ) {
        // App Bar
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 12.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(
                onClick = { navController.popBackStack() },
                modifier = Modifier
                    .size(40.dp)
                    .clip(CircleShape)
                    .background(Color.White)
                    .border(1.dp, GlassBorderLight, CircleShape)
            ) {
                Icon(Icons.Filled.ArrowBack, contentDescription = "Back", tint = TvsNavy)
            }
            Spacer(Modifier.width(12.dp))
            Column {
                Text(
                    "Trust Receipts / Audit Log",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = TvsNavy
                )
                Text(
                    text = "IMMUTABLE CRYPTOGRAPHIC ATTESTATIONS",
                    fontSize = 10.sp,
                    fontWeight = FontWeight.ExtraBold,
                    letterSpacing = 1.sp,
                    color = TvsGreenDark
                )
            }
        }

        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 20.dp, vertical = 12.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            item {
                Text(
                    "CRYPTOGRAPHIC AUDIT LOG",
                    color = TvsGreenDark,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.ExtraBold,
                    letterSpacing = 1.sp
                )
                Spacer(Modifier.height(4.dp))
                Text(
                    "Every genuine and intercepted interaction concerning your TVS account produces an attested record.",
                    color = TextMuted,
                    fontSize = 12.sp,
                    lineHeight = 16.sp
                )
            }

            if (history.isEmpty()) {
                item {
                    GlassCard {
                        Text(
                            "No interaction receipts on record yet.",
                            color = TvsNavy,
                            fontWeight = FontWeight.Bold,
                            fontSize = 14.sp
                        )
                        Text(
                            "When TVS contacts you or an action is gated, the attested receipt will appear here.",
                            color = TextMuted,
                            fontSize = 11.sp,
                            modifier = Modifier.padding(top = 4.dp)
                        )
                    }
                }
            }

            items(history) { r ->
                val isAllowed = r.decision == "ALLOWED"
                val accentColor = if (isAllowed) TvsGreen else AlertRed
                val textColor = if (isAllowed) TvsGreenDark else AlertRed

                GlassCard(
                    borderColor = if (isAllowed) Color(0xFF86EFAC) else Color(0xFFFECACA),
                    glowColor = if (isAllowed) Color(0x3300C853) else Color(0x33EF4444)
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier
                                .size(40.dp)
                                .clip(CircleShape)
                                .background(if (isAllowed) Color(0xFFDCFCE7) else Color(0xFFFEE2E2))
                                .border(1.dp, accentColor, CircleShape),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                if (isAllowed) Icons.Filled.CheckCircle else Icons.Filled.GppBad,
                                contentDescription = null,
                                tint = accentColor,
                                modifier = Modifier.size(22.dp)
                            )
                        }
                        Spacer(Modifier.width(12.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = if (isAllowed) "Interaction Authenticated" else "Interaction Blocked",
                                color = TvsNavy,
                                fontWeight = FontWeight.Bold,
                                fontSize = 13.sp
                            )
                            Text(
                                text = r.receiptId,
                                color = TextMuted,
                                fontSize = 11.sp,
                                fontFamily = FontFamily.Monospace
                            )
                        }
                        GlassChip(text = r.decision, color = textColor)
                    }

                    Spacer(Modifier.height(12.dp))
                    LabelValueRow("Action", r.action)
                    LabelValueRow("Amount", "₹${r.amount.toInt()}", valueColor = TvsNavy)
                    LabelValueRow("Destination", r.destination ?: "N/A", isMono = true, valueColor = if (isAllowed) TvsGreenDark else AlertRed)
                    LabelValueRow("Time", r.timestamp.substringBefore("T"))
                }
            }

            item {
                LoadingOverlay(viewModel.isLoading)
                Spacer(Modifier.height(16.dp))
            }
        }
    }
}
