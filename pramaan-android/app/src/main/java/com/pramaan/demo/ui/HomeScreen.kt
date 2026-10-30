package com.pramaan.demo.ui

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
import androidx.compose.material.icons.filled.ArrowForward
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Fingerprint
import androidx.compose.material.icons.filled.History
import androidx.compose.material.icons.filled.Language
import androidx.compose.material.icons.filled.NotificationsActive
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import com.pramaan.demo.PramaanViewModel
import com.pramaan.demo.ui.theme.AlertRed
import com.pramaan.demo.ui.theme.CanvasGlowMid
import com.pramaan.demo.ui.theme.CanvasGlowTop
import com.pramaan.demo.ui.theme.CanvasLightBg
import com.pramaan.demo.ui.theme.CanvasWhite
import com.pramaan.demo.ui.theme.GlassBorderLight
import com.pramaan.demo.ui.theme.GlassBorderMint
import com.pramaan.demo.ui.theme.GlassFillWhite
import com.pramaan.demo.ui.theme.NeonMint
import com.pramaan.demo.ui.theme.OrbBlue
import com.pramaan.demo.ui.theme.OrbOrange
import com.pramaan.demo.ui.theme.TextMint
import com.pramaan.demo.ui.theme.TextMuted
import com.pramaan.demo.ui.theme.TextPrimary
import com.pramaan.demo.ui.theme.TextWhite
import com.pramaan.demo.ui.theme.TvsGreen
import com.pramaan.demo.ui.theme.TvsGreenDark
import com.pramaan.demo.ui.theme.TvsNavy

@Composable
fun HomeScreen(navController: NavHostController, viewModel: PramaanViewModel = viewModel()) {
    LaunchedEffect(Unit) {
        viewModel.loadCustomerAccount()
        while (isActive) {
            viewModel.checkForIncomingInteraction()
            viewModel.loadReceiptHistory()
            delay(2500)
        }
    }

    val account = viewModel.account
    val activeIntent = viewModel.activeIntent
    val isHindi = viewModel.isRuralMode && viewModel.ruralLanguage == "hi"

    // TVS Credit E.P.I.C 6 Minimalist White & Glassmorphism Canvas
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
        // TVS Credit Glassmorphic Top Brand Banner
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 20.dp, vertical = 14.dp)
        ) {
            GlassCard(
                backgroundColor = Color.White,
                borderColor = GlassBorderLight,
                glowColor = GlassBorderMint,
                cornerRadius = 24
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            androidx.compose.foundation.Image(
                                painter = androidx.compose.ui.res.painterResource(id = com.pramaan.demo.R.drawable.tvs_credit_logo),
                                contentDescription = "TVS Credit",
                                modifier = Modifier.height(20.dp)
                            )
                            Spacer(Modifier.width(10.dp))
                            SecurityStatusBadge(
                                status = if (isHindi) "फ़ायरवॉल सक्रिय" else "FIREWALL ACTIVE",
                                color = TvsGreenDark
                            )
                        }
                        Spacer(Modifier.height(6.dp))
                        Text(
                            text = account?.customerName ?: "Krish Ray",
                            style = MaterialTheme.typography.headlineSmall,
                            color = TvsNavy,
                            fontWeight = FontWeight.ExtraBold,
                        )
                        Text(
                            text = "${if (isHindi) "ग्राहक संदर्भ" else "Customer Reference"}: ${account?.customerId ?: "CUST-001"}",
                            color = TextMuted,
                            fontSize = 12.sp,
                            fontFamily = FontFamily.Monospace
                        )
                    }
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(12.dp))
                                .background(Color(0xFFF1F5F9))
                                .border(1.dp, GlassBorderLight, RoundedCornerShape(12.dp))
                                .clickable { viewModel.resetDemoState() }
                                .padding(horizontal = 10.dp, vertical = 7.dp)
                        ) {
                            Text(
                                text = "RESET",
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Black,
                                color = TextMuted,
                                letterSpacing = 1.sp
                            )
                        }
                        IconButton(
                            onClick = {
                                viewModel.loadCustomerAccount()
                                viewModel.checkForIncomingInteraction()
                                viewModel.loadReceiptHistory()
                            },
                            modifier = Modifier
                                .clip(CircleShape)
                                .background(Color(0xFFF1F5F9))
                                .border(1.dp, GlassBorderLight, CircleShape)
                        ) {
                            Icon(Icons.Filled.Refresh, contentDescription = "Refresh", tint = TvsGreen)
                        }
                    }
                }

                Spacer(Modifier.height(14.dp))

                // Assisted Accessibility / Language Switch Bar
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(14.dp))
                        .background(Color(0xFFF8FAFC))
                        .border(1.dp, GlassBorderLight, RoundedCornerShape(14.dp))
                        .padding(horizontal = 14.dp, vertical = 8.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            Icons.Filled.Language,
                            contentDescription = null,
                            tint = TvsGreen,
                            modifier = Modifier.size(18.dp)
                        )
                        Spacer(Modifier.width(8.dp))
                        Column {
                            Text(
                                if (viewModel.isRuralMode) "सहायक सुरक्षा मोड (Assisted Mode)" else "Assisted Security Mode",
                                color = TvsNavy,
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                if (isHindi) "सरल भाषा एवं आवाज़ निर्देश" else "Simple wording & voice readout",
                                color = TextMuted,
                                fontSize = 10.sp
                            )
                        }
                    }

                    Row(verticalAlignment = Alignment.CenterVertically) {
                        if (viewModel.isRuralMode) {
                            Box(
                                modifier = Modifier
                                    .clip(RoundedCornerShape(8.dp))
                                    .background(Color(0xFFDCFCE7))
                                    .border(1.dp, Color(0xFF86EFAC), RoundedCornerShape(8.dp))
                                    .clickable {
                                        viewModel.setRuralLang(if (isHindi) "EN" else "HI")
                                    }
                                    .padding(horizontal = 8.dp, vertical = 4.dp)
                            ) {
                                Text(
                                    if (isHindi) "हिन्दी" else "ENG",
                                    color = TvsGreenDark,
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.ExtraBold
                                )
                            }
                            Spacer(Modifier.width(8.dp))
                        }

                        Switch(
                            checked = viewModel.isRuralMode,
                            onCheckedChange = { viewModel.toggleRuralMode() },
                            colors = SwitchDefaults.colors(
                                checkedThumbColor = Color.White,
                                checkedTrackColor = TvsGreen,
                                uncheckedThumbColor = Color.White,
                                uncheckedTrackColor = Color(0xFFCBD5E1)
                            )
                        )
                    }
                }
            }
        }

        // Section: Active TVS Interaction (Hero Journey Entry Point)
        Column(
            modifier = Modifier.padding(horizontal = 20.dp, vertical = 6.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            if (activeIntent != null) {
                // Incoming Interaction Waiting for Verification
                GlassCard(
                    backgroundColor = Color(0xFFF0FDF4),
                    borderColor = Color(0xFF86EFAC),
                    glowColor = Color(0x6600C853),
                    cornerRadius = 24
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Box(
                                modifier = Modifier
                                    .size(38.dp)
                                    .clip(CircleShape)
                                    .background(Color(0xFFDCFCE7)),
                                contentAlignment = Alignment.Center
                            ) {
                                Icon(
                                    Icons.Filled.NotificationsActive,
                                    contentDescription = null,
                                    tint = TvsGreen,
                                    modifier = Modifier.size(20.dp)
                                )
                            }
                            Spacer(Modifier.width(10.dp))
                            Column {
                                Text(
                                    text = if (isHindi) "TVS सक्रिय संपर्क अनुरोध" else "INCOMING INTERACTION",
                                    color = TvsGreenDark,
                                    fontWeight = FontWeight.ExtraBold,
                                    fontSize = 11.sp,
                                    letterSpacing = 1.sp
                                )
                                Text(
                                    text = if (isHindi) "सत्यापन एवं अनुमोदन आवश्यक" else "Action Verification Required",
                                    color = TvsNavy,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 14.sp
                                )
                            }
                        }

                        GlassChip(
                            text = "${activeIntent.expiresInSeconds}s",
                            color = OrbOrange
                        )
                    }

                    Spacer(Modifier.height(14.dp))

                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(14.dp))
                            .background(Color.White)
                            .border(1.dp, GlassBorderLight, RoundedCornerShape(14.dp))
                            .padding(14.dp)
                    ) {
                        Column {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    text = activeIntent.payload.purpose.replace("_", " ").uppercase(),
                                    color = TextMuted,
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold
                                )
                                Text(
                                    text = "₹${activeIntent.payload.amount.toInt()}",
                                    color = TvsNavy,
                                    fontWeight = FontWeight.ExtraBold,
                                    fontSize = 20.sp
                                )
                            }
                            Spacer(Modifier.height(6.dp))
                            Text(
                                text = "Recipient: ${activeIntent.payload.destination ?: "tvscredit.collections@upi"}",
                                color = TvsGreenDark,
                                fontSize = 12.sp,
                                fontFamily = FontFamily.Monospace,
                                fontWeight = FontWeight.Bold
                            )
                            Spacer(Modifier.height(2.dp))
                            Text(
                                text = "Agent: ${activeIntent.payload.agentName} (${activeIntent.payload.agentId})",
                                color = TextMuted,
                                fontSize = 11.sp
                            )
                        }
                    }

                    Spacer(Modifier.height(14.dp))

                    PrimaryButton(
                        text = if (isHindi) "सत्यापित करें और सुरक्षित रूप से आगे बढ़ें" else "Verify Securely (Exact Action Gate)",
                        containerColor = TvsGreen,
                        onClick = { navController.navigate("action_gate") }
                    )

                    Spacer(Modifier.height(8.dp))

                    SecondaryButton(
                        text = if (isHindi) "संपर्क विवरण देखें (Channel Details)" else "Inspect Interaction Details",
                        onClick = { navController.navigate("details") }
                    )
                }
            } else {
                // Idle Protected State Card
                GlassCard(
                    backgroundColor = Color.White,
                    borderColor = GlassBorderLight,
                    glowColor = Color(0x3300C853),
                    cornerRadius = 24
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier
                                .size(46.dp)
                                .clip(CircleShape)
                                .background(Color(0xFFDCFCE7))
                                .border(1.dp, Color(0xFF86EFAC), CircleShape),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                Icons.Filled.Shield,
                                contentDescription = null,
                                tint = TvsGreen,
                                modifier = Modifier.size(24.dp)
                            )
                        }
                        Spacer(Modifier.width(14.dp))
                        Column {
                            Text(
                                text = if (isHindi) "आपकी सुरक्षा सक्रिय है" else "Protection Active",
                                color = TvsNavy,
                                fontWeight = FontWeight.Bold,
                                fontSize = 15.sp
                            )
                            Text(
                                text = if (isHindi)
                                    "कोई अनधिकृत लेन-देन बिना आपकी मंज़ूरी के संभव नहीं है।"
                                else
                                    "No action unlocks without TVS cryptographic authorization.",
                                color = TextMuted,
                                fontSize = 12.sp
                            )
                        }
                    }
                }
            }

            // Loan Account Summary
            GlassCard(
                backgroundColor = Color.White,
                borderColor = GlassBorderLight,
                cornerRadius = 20
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        if (isHindi) "ऋण खाता विवरण" else "LOAN ACCOUNT PROTECTION",
                        color = TextMuted,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        letterSpacing = 1.sp
                    )
                    GlassChip(
                        text = account?.loanId ?: "LOAN-4521",
                        color = TvsNavy
                    )
                }

                Spacer(Modifier.height(14.dp))

                LabelValueRow(
                    label = if (isHindi) "ऋण प्रकार" else "Loan Facility",
                    value = account?.productName ?: "TVS Two-Wheeler Loan",
                    valueColor = TvsNavy
                )
                LabelValueRow(
                    label = if (isHindi) "अगली किस्त (ईएमआई)" else "Next EMI Due",
                    value = "₹${account?.amount?.toInt() ?: 3200}",
                    valueColor = TvsGreenDark
                )
                LabelValueRow(
                    label = if (isHindi) "अधिकृत वीपीए (VPA)" else "Authorized TVS VPA",
                    value = account?.authorizedDestination ?: "tvscredit.collections@upi",
                    valueColor = TvsNavy,
                    isMono = true
                )
                LabelValueRow(
                    label = if (isHindi) "सुरक्षा नीति" else "Gate Enforcement",
                    value = "Exact Action Gate Active",
                    valueColor = TvsGreenDark
                )
            }

            // Trust Receipts Live Section (Never Empty)
            GlassCard(
                backgroundColor = Color.White,
                borderColor = GlassBorderLight,
                glowColor = Color(0x3300C853),
                cornerRadius = 20,
                modifier = Modifier.clickable { navController.navigate("history") }
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier
                                .size(40.dp)
                                .clip(CircleShape)
                                .background(Color(0xFFDCFCE7)),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                Icons.Filled.History,
                                contentDescription = null,
                                tint = TvsGreen,
                                modifier = Modifier.size(20.dp)
                            )
                        }
                        Spacer(Modifier.width(12.dp))
                        Column {
                            Text(
                                if (isHindi) "डिजिटल विश्वास रसीदें" else "Cryptographic Trust Receipts",
                                fontWeight = FontWeight.Bold,
                                color = TvsNavy,
                                fontSize = 14.sp
                            )
                            Text(
                                if (isHindi)
                                    "सत्यापित लेन-देन का डिजिटल ऑडिट रिकॉर्ड"
                                else
                                    "Immutable cryptographic audit log",
                                color = TextMuted,
                                fontSize = 11.sp
                            )
                        }
                    }

                    Row(verticalAlignment = Alignment.CenterVertically) {
                        GlassChip(
                            text = "${viewModel.receiptsHistory.size} RECORDS",
                            color = TvsGreenDark
                        )
                        Spacer(Modifier.width(6.dp))
                        Icon(Icons.Filled.ArrowForward, contentDescription = null, tint = TextMuted, modifier = Modifier.size(18.dp))
                    }
                }

                // Recent Receipt Preview
                if (viewModel.receiptsHistory.isNotEmpty()) {
                    Spacer(Modifier.height(12.dp))
                    val latest = viewModel.receiptsHistory.first()
                    val isAllowed = latest.decision == "ALLOWED"
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(12.dp))
                            .background(Color(0xFFF8FAFC))
                            .border(1.dp, GlassBorderLight, RoundedCornerShape(12.dp))
                            .padding(12.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Icon(
                                        Icons.Filled.CheckCircle,
                                        contentDescription = null,
                                        tint = if (isAllowed) TvsGreen else AlertRed,
                                        modifier = Modifier.size(16.dp)
                                    )
                                    Spacer(Modifier.width(6.dp))
                                    Text(
                                        latest.receiptId,
                                        color = TvsNavy,
                                        fontSize = 12.sp,
                                        fontFamily = FontFamily.Monospace,
                                        fontWeight = FontWeight.Bold
                                    )
                                }
                                Text(
                                    "${latest.action.replace("_", " ").uppercase()} • ₹${latest.amount.toInt()}",
                                    color = TextMuted,
                                    fontSize = 11.sp
                                )
                            }
                            Text(
                                latest.decision,
                                color = if (isAllowed) TvsGreenDark else AlertRed,
                                fontSize = 11.sp,
                                fontWeight = FontWeight.ExtraBold
                            )
                        }
                    }
                }
            }

            // Identity Protection & KYC Scan Card
            GlassCard(
                backgroundColor = Color.White,
                borderColor = GlassBorderLight,
                cornerRadius = 20,
                modifier = Modifier.clickable { navController.navigate("kyc") }
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier
                                .size(40.dp)
                                .clip(CircleShape)
                                .background(Color(0xFFE0F2FE)),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                Icons.Filled.Fingerprint,
                                contentDescription = null,
                                tint = OrbBlue,
                                modifier = Modifier.size(20.dp)
                            )
                        }
                        Spacer(Modifier.width(12.dp))
                        Column {
                            Text(
                                if (isHindi) "पहचान एवं मीडिया सुरक्षा" else "Media & KYC Authenticity",
                                fontWeight = FontWeight.Bold,
                                color = TvsNavy,
                                fontSize = 14.sp
                            )
                            Text(
                                if (isHindi)
                                    "पहचान पत्रों और चेहरे की प्रामाणिकता जांच"
                                else
                                    "Document & face authenticity check (Inward Trust)",
                                color = TextMuted,
                                fontSize = 11.sp
                            )
                        }
                    }
                    Icon(Icons.Filled.ArrowForward, contentDescription = null, tint = TextMuted, modifier = Modifier.size(18.dp))
                }
            }

            Spacer(Modifier.height(20.dp))
            LoadingOverlay(viewModel.isLoading)
        }
    }

    // High-Visibility Modal Popup: Triggers immediately when TVS capability intent is detected
    if (viewModel.showIntentPopup && activeIntent != null) {
        Dialog(
            onDismissRequest = { viewModel.dismissIntentPopup() },
            properties = DialogProperties(dismissOnBackPress = true, dismissOnClickOutside = false)
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(28.dp))
                    .background(Color.White)
                    .border(1.5.dp, Color(0xFF00C853).copy(alpha = 0.6f), RoundedCornerShape(28.dp))
                    .shadow(elevation = 24.dp, shape = RoundedCornerShape(28.dp))
                    .padding(24.dp)
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    val isAttackScenario = activeIntent.payload.scenarioTag != null && activeIntent.payload.scenarioTag != "genuine"
                    val scenarioTitle = activeIntent.payload.scenarioTitle ?: (if (isHindi) "TVS सक्रिय संपर्क अनुरोध" else "OFFICIAL TVS CONTACT DETECTED")

                    Box(
                        modifier = Modifier
                            .size(60.dp)
                            .clip(CircleShape)
                            .background(if (isAttackScenario) Color(0xFFFEE2E2) else Color(0xFFDCFCE7))
                            .border(2.dp, if (isAttackScenario) AlertRed else TvsGreen, CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            if (isAttackScenario) Icons.Filled.Warning else Icons.Filled.NotificationsActive,
                            contentDescription = null,
                            tint = if (isAttackScenario) AlertRed else TvsGreenDark,
                            modifier = Modifier.size(30.dp)
                        )
                    }

                    Spacer(Modifier.height(14.dp))

                    Text(
                        text = if (isAttackScenario) "⚠️ $scenarioTitle"
                        else if (isHindi) "TVS सक्रिय संपर्क अनुरोध"
                        else "OFFICIAL TVS CONTACT DETECTED",
                        color = if (isAttackScenario) AlertRed else TvsNavy,
                        fontWeight = FontWeight.Black,
                        fontSize = 15.sp,
                        letterSpacing = 0.5.sp,
                        textAlign = TextAlign.Center
                    )

                    Spacer(Modifier.height(6.dp))

                    Text(
                        text = if (isAttackScenario)
                            "An interaction claim is requesting authorization on your account. Review parameters carefully before proceeding."
                        else if (isHindi)
                            "एक नया आधिकारिक वित्तीय संपर्क अनुरोध आपके खाते के लिए प्राप्त हुआ है।"
                        else
                            "A cryptographically verified interaction capability has been dispatched to your device.",
                        color = TextMuted,
                        fontSize = 12.sp,
                        textAlign = TextAlign.Center,
                        lineHeight = 16.sp
                    )

                    Spacer(Modifier.height(16.dp))

                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(16.dp))
                            .background(Color(0xFFF8FAFC))
                            .border(1.dp, GlassBorderLight, RoundedCornerShape(16.dp))
                            .padding(14.dp)
                    ) {
                        Column {
                            val displayAmount = activeIntent.payload.claimedAmount ?: activeIntent.payload.amount
                            val displayDest = activeIntent.payload.claimedDestination ?: (activeIntent.payload.destination ?: "tvscredit.collections@upi")

                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    text = activeIntent.payload.purpose.replace("_", " ").uppercase(),
                                    color = if (isAttackScenario) AlertRed else TvsGreenDark,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 11.sp
                                )
                                Text(
                                    text = "₹${displayAmount.toInt()}",
                                    color = if (isAttackScenario && displayAmount != activeIntent.payload.amount) AlertRed else TvsNavy,
                                    fontWeight = FontWeight.ExtraBold,
                                    fontSize = 20.sp
                                )
                            }
                            Spacer(Modifier.height(8.dp))
                            Text(
                                text = "Recipient: $displayDest",
                                color = if (isAttackScenario && displayDest != (activeIntent.payload.destination ?: "tvscredit.collections@upi")) AlertRed else TextMuted,
                                fontSize = 11.sp,
                                fontFamily = FontFamily.Monospace,
                                fontWeight = FontWeight.SemiBold
                            )
                            Spacer(Modifier.height(4.dp))
                            Text(
                                text = "Agent: ${activeIntent.payload.agentName} (${activeIntent.payload.claimedAgentId ?: activeIntent.payload.agentId})",
                                color = TextMuted,
                                fontSize = 11.sp
                            )
                        }
                    }

                    Spacer(Modifier.height(18.dp))

                    PrimaryButton(
                        text = if (isHindi) "सत्यापित करें (Exact Action Gate)" else "🛡️ Verify on Exact Action Gate",
                        containerColor = TvsGreen,
                        onClick = {
                            viewModel.dismissIntentPopup()
                            navController.navigate("action_gate")
                        }
                    )

                    Spacer(Modifier.height(10.dp))

                    SecondaryButton(
                        text = if (isHindi) "सुरक्षा विवरण देखें (View Handoff)" else "🔍 View Cryptographic Details",
                        onClick = {
                            viewModel.dismissIntentPopup()
                            navController.navigate("handoff")
                        }
                    )

                    Spacer(Modifier.height(10.dp))

                    Text(
                        text = if (isHindi) "बाद में देखें (Dismiss)" else "Review on Dashboard Later",
                        color = TextMuted,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.SemiBold,
                        modifier = Modifier
                            .clip(RoundedCornerShape(8.dp))
                            .clickable { viewModel.dismissIntentPopup() }
                            .padding(horizontal = 12.dp, vertical = 6.dp)
                    )
                }
            }
        }
    }
}
