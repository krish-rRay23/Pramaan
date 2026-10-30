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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
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
import com.pramaan.demo.ui.theme.OrbBlue
import com.pramaan.demo.ui.theme.OrbOrange
import com.pramaan.demo.ui.theme.TextMint
import com.pramaan.demo.ui.theme.TextMuted
import com.pramaan.demo.ui.theme.TextPrimary
import com.pramaan.demo.ui.theme.TvsGreen
import com.pramaan.demo.ui.theme.TvsGreenDark
import com.pramaan.demo.ui.theme.TvsNavy

@Composable
fun InteractionDetailsScreen(
    navController: NavHostController,
    viewModel: PramaanViewModel = viewModel(),
) {
    val intent = viewModel.activeIntent
    val isHindi = viewModel.isRuralMode && viewModel.ruralLanguage == "hi"

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
            .statusBarsPadding()
            .verticalScroll(rememberScrollState()),
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
                    text = if (isHindi) "इंटरैक्शन विवरण एवं प्राधिकार" else "Interaction Details & Capability",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = TvsNavy
                )
                Text(
                    text = "AUTHORIZATION POLICY INSPECTION",
                    fontSize = 10.sp,
                    fontWeight = FontWeight.ExtraBold,
                    letterSpacing = 1.sp,
                    color = TvsGreenDark
                )
            }
        }

        if (intent == null) {
            Column(
                modifier = Modifier.padding(20.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                GlassCard {
                    Text(
                        if (isHindi) "कोई सक्रिय लेन-देन नहीं मिला।" else "No active interaction loaded.",
                        color = TextMuted
                    )
                    Spacer(Modifier.height(12.dp))
                    SecondaryButton(if (isHindi) "होम पर लौटें" else "Return to Home") {
                        navController.popBackStack()
                    }
                }
            }
        } else {
            Column(
                modifier = Modifier.padding(20.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Trust Attestation Card
                GlassCard(
                    borderColor = Color(0xFF86EFAC),
                    glowColor = Color(0x3300C853)
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier
                                .size(40.dp)
                                .clip(CircleShape)
                                .background(Color(0xFFDCFCE7))
                                .border(1.dp, TvsGreen, CircleShape),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(Icons.Filled.Shield, contentDescription = null, tint = TvsGreen, modifier = Modifier.size(22.dp))
                        }
                        Spacer(Modifier.width(12.dp))
                        Column {
                            Text(
                                if (isHindi) "TVS क्रेडिट द्वारा डिजिटल हस्ताक्षरित" else "Cryptographically Signed by TVS Credit",
                                color = TvsNavy,
                                fontWeight = FontWeight.Bold,
                                fontSize = 13.sp
                            )
                            Text(
                                "Intent ID: ${intent.payload.intentId}",
                                color = TvsGreenDark,
                                fontSize = 11.sp,
                                fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace
                            )
                        }
                    }
                }

                // Section 1: WHO AUTHORIZED THIS? (Partner & Agent Capability)
                GlassCard {
                    Text(
                        if (isHindi) "किसने अधिकृत किया? (पार्टनर एवं एजेंट क्षमता)" else "WHO AUTHORIZED THIS? (PARTNER & AGENT CAPABILITY)",
                        color = TextMuted,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        letterSpacing = 1.sp
                    )
                    Spacer(Modifier.height(12.dp))
                    LabelValueRow(if (isHindi) "संस्थान" else "Organization", "TVS Credit Services Ltd.")
                    LabelValueRow(if (isHindi) "पार्टनर / एलएसपी" else "Partner / LSP", intent.payload.partnerName)
                    LabelValueRow(if (isHindi) "अधिकृत एजेंट" else "Authorized Agent", intent.payload.agentName)
                    LabelValueRow(if (isHindi) "एजेंट आईडी" else "Agent Employee ID", intent.payload.agentId, isMono = true)
                    LabelValueRow(if (isHindi) "अनुमति प्राप्त कार्रवाई" else "Permitted Capability", intent.payload.action)
                    LabelValueRow(if (isHindi) "संचार चैनल" else "Outbound Channel", intent.payload.channel.uppercase())
                }

                // Section 2: WHAT IS BEING REQUESTED?
                GlassCard {
                    Text(
                        if (isHindi) "क्या अनुरोध किया जा रहा है?" else "WHAT IS BEING REQUESTED?",
                        color = TextMuted,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        letterSpacing = 1.sp
                    )
                    Spacer(Modifier.height(12.dp))
                    LabelValueRow(if (isHindi) "ऋण खाता" else "Loan Account", intent.payload.loanId, isMono = true)
                    LabelValueRow(if (isHindi) "उद्देश्य" else "Purpose", intent.payload.purpose.replace("_", " ").uppercase())
                    LabelValueRow(
                        label = if (isHindi) "अधिकृत राशि" else "Authorized Amount",
                        value = "₹${intent.payload.amount.toInt()}",
                        valueColor = TvsNavy
                    )
                    LabelValueRow(
                        label = if (isHindi) "अधिकृत गंतव्य" else "Authorized Destination",
                        value = intent.payload.destination ?: "N/A",
                        valueColor = TvsGreenDark,
                        isMono = true
                    )
                }

                // Section 3: TIMING & POLICY BOUNDARIES
                GlassCard {
                    Text(
                        if (isHindi) "सुरक्षा नीति एवं वैधता" else "SECURITY POLICY & EXPIRY",
                        color = TextMuted,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        letterSpacing = 1.sp
                    )
                    Spacer(Modifier.height(12.dp))
                    LabelValueRow(if (isHindi) "शेष समय" else "Remaining Validity", "${intent.expiresInSeconds}s active")
                    LabelValueRow(if (isHindi) "सटीक कार्रवाई द्वार" else "Exact Action Gate", "Enforced", valueColor = TvsGreenDark)
                    LabelValueRow(if (isHindi) "रीप्ले सुरक्षा" else "Replay Protection", "Single-Use Nonce Bound", valueColor = TvsGreenDark)
                }

                Spacer(Modifier.height(6.dp))

                PrimaryButton(
                    text = if (isHindi) "सटीक कार्रवाई द्वार पर जाएं" else "Proceed to Exact Action Gate",
                    containerColor = TvsGreen,
                    onClick = { navController.navigate("action_gate") }
                )

                // Customer Kill Switch
                DangerButton(
                    text = if (isHindi) "मुझे इस अनुरोध पर भरोसा नहीं है" else "I DON'T TRUST THIS REQUEST",
                    onClick = {
                        viewModel.triggerKillSwitch {
                            navController.navigate("kill_switch_report") {
                                popUpTo("home") { inclusive = false }
                            }
                        }
                    }
                )

                SecondaryButton(
                    text = if (isHindi) "वापस जाएं" else "Back to Home",
                    onClick = { navController.popBackStack() }
                )

                Spacer(Modifier.height(16.dp))
            }
        }
    }
}
