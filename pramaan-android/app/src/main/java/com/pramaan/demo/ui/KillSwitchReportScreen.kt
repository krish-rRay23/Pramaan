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
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Phone
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material3.Icon
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
import com.pramaan.demo.ui.theme.CanvasLightBg
import com.pramaan.demo.ui.theme.CanvasWhite
import com.pramaan.demo.ui.theme.GlassBorderLight
import com.pramaan.demo.ui.theme.TextMint
import com.pramaan.demo.ui.theme.TextMuted
import com.pramaan.demo.ui.theme.TextPrimary
import com.pramaan.demo.ui.theme.TextWhite
import com.pramaan.demo.ui.theme.TvsGreen
import com.pramaan.demo.ui.theme.TvsGreenDark
import com.pramaan.demo.ui.theme.TvsNavy

@Composable
fun KillSwitchReportScreen(
    navController: NavHostController,
    viewModel: PramaanViewModel = viewModel(),
) {
    val killSwitchResp = viewModel.lastKillSwitchResponse
    val isHindi = viewModel.isRuralMode && viewModel.ruralLanguage == "hi"

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
        // Red Shield Header (Glassmorphic White)
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
                        Icons.Filled.Shield,
                        contentDescription = null,
                        tint = AlertRed,
                        modifier = Modifier.size(48.dp)
                    )
                }
                Spacer(Modifier.height(16.dp))
                Text(
                    text = if (isHindi) "लेन-देन रद्द और सुरक्षा सक्रिय" else "TRANSACTION SHIELD DEPLOYED",
                    color = TvsNavy,
                    fontWeight = FontWeight.ExtraBold,
                    fontSize = 18.sp,
                    letterSpacing = 0.8.sp
                )
                Spacer(Modifier.height(4.dp))
                Text(
                    text = if (isHindi)
                        "TVS क्रेडिट धोखाधड़ी सुरक्षा प्रणाली ने इस अनुरोध को तुरंत रद्द कर दिया है।"
                    else
                        "TVS Credit Financial Firewall has revoked and quarantined this interaction.",
                    color = AlertRed,
                    fontWeight = FontWeight.Medium,
                    fontSize = 12.sp,
                )
            }
        }

        Column(
            modifier = Modifier.padding(horizontal = 20.dp, vertical = 4.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Incident Confirmation Card (GlassCard White)
            GlassCard(
                borderColor = Color(0xFFFECACA),
                glowColor = Color(0x40EF4444)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        if (isHindi) "धोखाधड़ी रोकथाम रिपोर्ट" else "FRAUD INCIDENT REPORT",
                        color = AlertRed,
                        fontWeight = FontWeight.ExtraBold,
                        fontSize = 11.sp,
                        letterSpacing = 1.sp
                    )
                    GlassChip(
                        text = "BLOCKED & QUARANTINED",
                        color = AlertRed
                    )
                }

                Spacer(Modifier.height(16.dp))
                LabelValueRow(
                    label = if (isHindi) "घटना संदर्भ आईडी" else "Incident ID",
                    value = killSwitchResp?.incidentId ?: "INC-AUTO-REPORT",
                    isMono = true,
                    valueColor = AlertRed
                )
                LabelValueRow(
                    label = if (isHindi) "सुरक्षा स्थिति" else "Firewall Status",
                    value = killSwitchResp?.status?.uppercase() ?: "REVOKED_BY_CUSTOMER",
                    valueColor = AlertRed
                )
                LabelValueRow(
                    label = if (isHindi) "संगरोध गंतव्य" else "Quarantined Destination",
                    value = killSwitchResp?.quarantinedDestination ?: "tvscredit.collections@upi",
                    valueColor = TvsNavy,
                    isMono = true
                )
                LabelValueRow(
                    label = if (isHindi) "रद्द किया गया इरादा" else "Revoked Intent",
                    value = killSwitchResp?.revokedIntentId ?: "ACTIVE_SESSION",
                    valueColor = TvsNavy,
                    isMono = true
                )
                LabelValueRow(
                    label = if (isHindi) "टाइमस्टैम्प" else "Timestamp",
                    value = killSwitchResp?.timestamp?.substringBefore(".") ?: "Just now"
                )
            }

            // Customer Safety Guarantee Card (GlassCard White)
            GlassCard(
                borderColor = Color(0xFF86EFAC),
                glowColor = Color(0x3300C853)
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Filled.CheckCircle, contentDescription = null, tint = TvsGreen)
                    Spacer(Modifier.width(10.dp))
                    Text(
                        if (isHindi) "आपका खाता सुरक्षित है" else "Your Account Is Protected",
                        fontWeight = FontWeight.ExtraBold,
                        color = TvsGreenDark,
                        fontSize = 14.sp
                    )
                }
                Spacer(Modifier.height(8.dp))
                Text(
                    text = if (isHindi)
                        "• कोई भी धनराशि हस्तांतरित नहीं की गई है।\n• संदिग्ध प्राप्तकर्ता को सभी TVS क्रेडिट प्रणालियों पर ब्लैकलिस्ट कर दिया गया है।\n• हमारे धोखाधड़ी विश्लेषण दल को सूचित कर दिया गया है।"
                    else
                        "• Zero funds were debited from your account.\n• The suspicious destination has been quarantined in the Operations Console.\n• TVS Credit fraud prevention team has been automatically notified.",
                    color = TextPrimary,
                    fontSize = 12.sp,
                    lineHeight = 18.sp
                )
            }

            // Emergency Helpline (GlassCard White)
            GlassCard {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(36.dp)
                            .clip(CircleShape)
                            .background(Color(0xFFF1F5F9)),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(Icons.Filled.Phone, contentDescription = null, tint = TvsNavy, modifier = Modifier.size(20.dp))
                    }
                    Spacer(Modifier.width(12.dp))
                    Column {
                        Text(
                            if (isHindi) "TVS क्रेडिट आपातकालीन सहायता" else "TVS Credit Emergency Helpline",
                            fontWeight = FontWeight.Bold,
                            color = TvsNavy,
                            fontSize = 13.sp
                        )
                        Text(
                            "1800-425-4521 (Toll Free • 24x7 Fraud Support)",
                            color = TvsGreenDark,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.SemiBold
                        )
                    }
                }
            }

            Spacer(Modifier.height(8.dp))

            PrimaryButton(
                text = if (isHindi) "सुरक्षित होम पर लौटें" else "Return to Safe Home",
                containerColor = TvsGreen,
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
