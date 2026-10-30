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
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Chat
import androidx.compose.material.icons.filled.PhoneInTalk
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
import com.pramaan.demo.ui.theme.OrbBlue
import com.pramaan.demo.ui.theme.OrbOrange
import com.pramaan.demo.ui.theme.TextMint
import com.pramaan.demo.ui.theme.TextMuted
import com.pramaan.demo.ui.theme.TextPrimary
import com.pramaan.demo.ui.theme.TvsGreen
import com.pramaan.demo.ui.theme.TvsGreenDark
import com.pramaan.demo.ui.theme.TvsNavy

@Composable
fun TrustedHandoffScreen(
    navController: NavHostController,
    viewModel: PramaanViewModel = viewModel(),
) {
    val intent = viewModel.activeIntent
    val channel = viewModel.incomingChannel.ifBlank { intent?.payload?.channel ?: "whatsapp" }
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
                    text = if (isHindi) "विश्वसनीय हैंडऑफ (सुरक्षित प्रमाणीकरण)" else "Trusted Channel Handoff",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = TvsNavy
                )
                Text(
                    text = "UNTRUSTED CHANNEL ISOLATION",
                    fontSize = 10.sp,
                    fontWeight = FontWeight.ExtraBold,
                    letterSpacing = 1.sp,
                    color = TvsGreenDark
                )
            }
        }

        // Channel Handoff Hero Banner (Glassmorphic White)
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 20.dp, vertical = 8.dp)
                .clip(RoundedCornerShape(24.dp))
                .background(Color.White)
                .border(1.dp, Color(0xFF86EFAC), RoundedCornerShape(24.dp))
                .padding(24.dp)
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.fillMaxWidth()) {
                Box(
                    modifier = Modifier
                        .size(68.dp)
                        .clip(CircleShape)
                        .background(
                            if (channel.contains("call", true)) Color(0xFFE0F2FE) else Color(0xFFFFEDD5)
                        )
                        .border(
                            1.dp,
                            if (channel.contains("call", true)) OrbBlue else OrbOrange,
                            CircleShape
                        ),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        if (channel.contains("call", true)) Icons.Filled.PhoneInTalk else Icons.Filled.Chat,
                        contentDescription = null,
                        tint = if (channel.contains("call", true)) OrbBlue else OrbOrange,
                        modifier = Modifier.size(36.dp)
                    )
                }
                Spacer(Modifier.height(14.dp))
                Text(
                    text = if (isHindi) "TVS क्रेडिट में सुरक्षित रूप से जारी रखें" else "Continue Securely in TVS Credit",
                    color = TvsNavy,
                    fontWeight = FontWeight.ExtraBold,
                    fontSize = 18.sp
                )
                Spacer(Modifier.height(6.dp))
                Text(
                    text = if (isHindi)
                        "असुरक्षित चैनल (${channel.uppercase()}) से लेन-देन को वित्तीय फ़ायरवॉल में स्थानांतरित किया गया।"
                    else
                        "Transaction handoff from untrusted ${channel.uppercase()} into the TVS financial-interaction firewall.",
                    color = TextMuted,
                    fontSize = 12.sp,
                    lineHeight = 17.sp,
                    textAlign = androidx.compose.ui.text.style.TextAlign.Center
                )
            }
        }

        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Channel Context Card
            GlassCard {
                Text(
                    if (isHindi) "मूल संचार चैनल" else "ORIGINATING CONTACT CHANNEL",
                    color = TextMuted,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 1.sp
                )
                Spacer(Modifier.height(10.dp))
                LabelValueRow(
                    if (isHindi) "चैनल" else "Origin Channel",
                    channel.uppercase(),
                    valueColor = TvsNavy
                )
                LabelValueRow(
                    if (isHindi) "स्थिति" else "Security Status",
                    if (isHindi) "सत्यापन लंबित" else "Isolated for Verification",
                    valueColor = OrbOrange
                )
                LabelValueRow(
                    if (isHindi) "सुरक्षा नीति" else "Protection Policy",
                    "PRAMAAN v3 Financial Gate Active",
                    valueColor = TvsGreenDark
                )
            }

            if (intent != null) {
                // Pending Intent Details
                GlassCard {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            if (isHindi) "TVS क्रेडिट द्वारा अधिकृत इरादा" else "TVS AUTHORIZED INTENT",
                            color = TvsGreenDark,
                            fontWeight = FontWeight.ExtraBold,
                            fontSize = 11.sp,
                            letterSpacing = 1.sp
                        )
                        GlassChip(text = "Ed25519 SIGNED", color = TvsGreenDark)
                    }
                    Spacer(Modifier.height(14.dp))
                    LabelValueRow(if (isHindi) "ऋण खाता" else "Loan Account", intent.payload.loanId, isMono = true)
                    LabelValueRow(if (isHindi) "उद्देश्य" else "Purpose", intent.payload.purpose.replace("_", " ").uppercase())
                    LabelValueRow(
                        label = if (isHindi) "अधिकृत राशि" else "Authorized Amount",
                        value = "₹${intent.payload.amount.toInt()}",
                        valueColor = TvsNavy
                    )
                    LabelValueRow(
                        label = if (isHindi) "अधिकृत प्राप्तकर्ता" else "Authorized Destination",
                        value = intent.payload.destination ?: "tvscredit.collections@upi",
                        valueColor = TvsGreenDark,
                        isMono = true
                    )
                    LabelValueRow(if (isHindi) "अधिकृत एजेंट" else "Authorized Agent", "${intent.payload.agentName} (${intent.payload.agentId})")
                }

                // Call to Action
                PrimaryButton(
                    text = if (isHindi) "सत्यापन और भुगतान द्वार पर जाएं" else "Proceed to Exact Action Gate",
                    containerColor = TvsGreen,
                    onClick = { navController.navigate("action_gate") }
                )

                // Secondary option: Inspect full details
                SecondaryButton(
                    text = if (isHindi) "विस्तृत विवरण देखें" else "View Detailed Intent Info",
                    onClick = { navController.navigate("details") }
                )

                Spacer(Modifier.height(4.dp))

                // Customer Kill Switch
                GlassCard(
                    borderColor = Color(0xFFFECACA),
                    glowColor = Color(0x40EF4444)
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Filled.Warning, contentDescription = null, tint = AlertRed)
                        Spacer(Modifier.width(10.dp))
                        Text(
                            if (isHindi) "संदिग्ध अनुरोध?" else "Suspicious of this contact?",
                            fontWeight = FontWeight.Bold,
                            color = AlertRed,
                            fontSize = 13.sp
                        )
                    }
                    Spacer(Modifier.height(8.dp))
                    Text(
                        if (isHindi)
                            "यदि आपने इस संदेश की उम्मीद नहीं की थी, तो तुरंत किल स्विच दबाएं।"
                        else
                            "If you did not initiate or expect this interaction, immediately activate the Kill Switch.",
                        color = TextMuted,
                        fontSize = 11.sp
                    )
                    Spacer(Modifier.height(14.dp))
                    DangerButton(
                        text = if (isHindi) "मुझे इस अनुरोध पर भरोसा नहीं है (किल स्विच)" else "I DON'T TRUST THIS REQUEST",
                        onClick = {
                            viewModel.triggerKillSwitch {
                                navController.navigate("kill_switch_report") {
                                    popUpTo("home") { inclusive = false }
                                }
                            }
                        }
                    )
                }
            } else {
                GlassCard {
                    Text(
                        if (isHindi) "कोई सक्रिय लेन-देन नहीं मिला।" else "No active interaction intent found for handoff.",
                        color = TextMuted
                    )
                    Spacer(Modifier.height(12.dp))
                    SecondaryButton(if (isHindi) "होम पर वापस जाएं" else "Return to Home") {
                        navController.navigate("home")
                    }
                }
            }
        }
    }
}
