package com.pramaan.demo.ui

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.expandVertically
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.shrinkVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
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
import androidx.compose.material.icons.filled.ExpandLess
import androidx.compose.material.icons.filled.ExpandMore
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.VerifiedUser
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
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
import com.pramaan.demo.ui.theme.CanvasGlowMid
import com.pramaan.demo.ui.theme.CanvasGlowTop
import com.pramaan.demo.ui.theme.CanvasLightBg
import com.pramaan.demo.ui.theme.CanvasWhite
import com.pramaan.demo.ui.theme.GlassBorderLight
import com.pramaan.demo.ui.theme.GlassBorderMint
import com.pramaan.demo.ui.theme.TextMint
import com.pramaan.demo.ui.theme.TextMuted
import com.pramaan.demo.ui.theme.TextPrimary
import com.pramaan.demo.ui.theme.TvsGreen
import com.pramaan.demo.ui.theme.TvsGreenDark
import com.pramaan.demo.ui.theme.TvsNavy

@Composable
fun TrustReceiptScreen(
    navController: NavHostController,
    viewModel: PramaanViewModel = viewModel(),
) {
    LaunchedEffect(Unit) {
        viewModel.loadReceiptHistory()
    }

    val receipt = viewModel.lastReceipt
    val isHindi = viewModel.isRuralMode && viewModel.ruralLanguage == "hi"
    var isProofExpanded by remember { mutableStateOf(false) }

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
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        // Emerald Attestation Header (Glassmorphic White)
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp)
                .clip(RoundedCornerShape(24.dp))
                .background(Color.White)
                .border(1.dp, Color(0xFF86EFAC), RoundedCornerShape(24.dp))
                .padding(28.dp),
            contentAlignment = Alignment.Center
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Box(
                    modifier = Modifier
                        .size(80.dp)
                        .clip(CircleShape)
                        .background(Color(0xFFDCFCE7))
                        .border(1.5.dp, TvsGreen, CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        Icons.Filled.VerifiedUser,
                        contentDescription = null,
                        tint = TvsGreen,
                        modifier = Modifier.size(48.dp)
                    )
                }
                Spacer(Modifier.height(16.dp))
                Text(
                    text = if (isHindi) "लेन-देन प्रमाणित एवं सुरक्षित" else "INTERACTION AUTHENTICATED",
                    color = TvsNavy,
                    fontWeight = FontWeight.ExtraBold,
                    fontSize = 18.sp,
                    letterSpacing = 0.8.sp
                )
                Spacer(Modifier.height(4.dp))
                Text(
                    text = if (isHindi)
                        "TVS क्रेडिट वित्तीय फ़ायरवॉल द्वारा सत्यापित"
                    else
                        "Cryptographically Attested by TVS Credit Financial Firewall",
                    color = TvsGreenDark,
                    fontWeight = FontWeight.Medium,
                    fontSize = 12.sp,
                )
            }
        }

        Column(
            modifier = Modifier.padding(horizontal = 20.dp, vertical = 4.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Receipt Content (GlassCard White)
            GlassCard(
                borderColor = Color(0xFF86EFAC),
                glowColor = Color(0x3300C853)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        if (isHindi) "सुरक्षा एवं विश्वास रसीद" else "SECURITY & TRUST RECEIPT",
                        color = TvsGreenDark,
                        fontWeight = FontWeight.ExtraBold,
                        fontSize = 11.sp,
                        letterSpacing = 1.sp
                    )
                    GlassChip(
                        text = receipt?.receiptId ?: "RCP-000000",
                        color = TvsGreenDark
                    )
                }

                Spacer(Modifier.height(16.dp))
                LabelValueRow(if (isHindi) "प्राधिकार संदर्भ" else "Authorization Ref", receipt?.authorizationRef ?: "TVS-AUTH-0000", isMono = true)
                LabelValueRow(if (isHindi) "ऋण खाता" else "Loan Account", receipt?.loanId ?: "LOAN-4521", isMono = true)
                LabelValueRow(if (isHindi) "ग्राहक संदर्भ" else "Customer Reference", receipt?.customerId ?: "CUST-001", isMono = true)
                LabelValueRow(if (isHindi) "अधिकृत कार्रवाई" else "Authorized Action", receipt?.action ?: "collect_payment")
                LabelValueRow(
                    label = if (isHindi) "सत्यापित राशि" else "Verified Amount",
                    value = "₹${receipt?.amount?.toInt() ?: 3200}",
                    valueColor = TvsGreenDark
                )
                LabelValueRow(
                    label = if (isHindi) "अधिकृत गंतव्य" else "Authorized Destination",
                    value = receipt?.destination ?: "tvscredit.collections@upi",
                    valueColor = TvsNavy,
                    isMono = true
                )
                LabelValueRow(if (isHindi) "सत्यापित एजेंट" else "Verified Agent", "${receipt?.agentName ?: "Suresh Menon"} (${receipt?.agentId ?: "AGT-7701"})")
                LabelValueRow(
                    label = if (isHindi) "अंतिम निर्णय" else "Final Decision",
                    value = receipt?.decision ?: "ALLOWED",
                    valueColor = TvsGreenDark
                )
                LabelValueRow(if (isHindi) "प्रमाणीकरण समय" else "Attestation Time", receipt?.timestamp?.substringBefore(".") ?: "Just now")
            }

            // Cryptographic Details Behind "View Proof" Collapsible
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(16.dp))
                    .background(Color.White)
                    .border(1.dp, GlassBorderLight, RoundedCornerShape(16.dp))
                    .clickable { isProofExpanded = !isProofExpanded }
                    .padding(16.dp)
            ) {
                Column {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Filled.Lock, contentDescription = null, tint = TvsGreen, modifier = Modifier.size(18.dp))
                            Spacer(Modifier.width(8.dp))
                            Text(
                                if (isHindi) "क्रिप्टोग्राफिक प्रमाण देखें (View Proof)" else "View Cryptographic Proof",
                                color = TvsNavy,
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                        Icon(
                            imageVector = if (isProofExpanded) Icons.Filled.ExpandLess else Icons.Filled.ExpandMore,
                            contentDescription = null,
                            tint = TextMuted
                        )
                    }

                    AnimatedVisibility(
                        visible = isProofExpanded,
                        enter = fadeIn() + expandVertically(),
                        exit = fadeOut() + shrinkVertically()
                    ) {
                        Column(modifier = Modifier.padding(top = 14.dp)) {
                            LabelValueRow("Signature Type", "Ed25519 Asymmetric (Curve25519)")
                            LabelValueRow("Key Authority ID", receipt?.keyId ?: "tvs-ed25519-master", isMono = true)
                            LabelValueRow("Policy Version", receipt?.policyVersion ?: "3.2.0")
                            LabelValueRow("Nonce Reference", "Single-Use Cryptographic Nonce", isMono = true)
                            Spacer(Modifier.height(8.dp))
                            Text(
                                "Digital Signature Hash:",
                                color = TextMuted,
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold
                            )
                            Spacer(Modifier.height(4.dp))
                            Text(
                                text = receipt?.signature ?: "7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
                                color = TvsGreenDark,
                                fontFamily = FontFamily.Monospace,
                                fontSize = 10.sp,
                                lineHeight = 14.sp
                            )
                            Spacer(Modifier.height(8.dp))
                            Text(
                                text = "Logged to TVS Credit Enterprise Immutable Audit Trail.",
                                color = TextMuted,
                                fontSize = 10.sp
                            )
                        }
                    }
                }
            }

            Spacer(Modifier.height(8.dp))

            PrimaryButton(
                text = if (isHindi) "पूर्ण और होम पर वापस जाएं" else "Done & Back to Home",
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
