package com.pramaan.demo.ui

import android.speech.tts.TextToSpeech
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
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.ExpandLess
import androidx.compose.material.icons.filled.ExpandMore
import androidx.compose.material.icons.filled.GppBad
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.VolumeUp
import androidx.compose.material3.Checkbox
import androidx.compose.material3.CheckboxDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
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
import com.pramaan.demo.ui.theme.GlassBorderMint
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
import java.util.Locale

@Composable
fun ExactActionGateScreen(
    navController: NavHostController,
    viewModel: PramaanViewModel = viewModel(),
) {
    val intent = viewModel.activeIntent
    val authorizedDestination = intent?.payload?.destination ?: "tvscredit.collections@upi"
    val requestedAmount = intent?.payload?.amount?.toInt() ?: 3200
    val requestedPurpose = intent?.payload?.purpose?.replace("_", " ")?.uppercase() ?: "EMI PAYMENT"

    val initialClaimedDest = intent?.payload?.claimedDestination ?: authorizedDestination
    var claimedDestination by remember(authorizedDestination, intent?.payload?.claimedDestination) {
        mutableStateOf(initialClaimedDest)
    }
    var isTechnicalDetailsExpanded by remember { mutableStateOf(false) }
    var highRiskConfirmed by remember { mutableStateOf(false) }
    var requiresStepUp by remember { mutableStateOf(false) }

    val isDestMatching = claimedDestination.trim().equals(authorizedDestination.trim(), ignoreCase = true)
    val isAmountMatching = intent?.payload?.claimedAmount == null || kotlin.math.abs(intent.payload.claimedAmount - intent.payload.amount) < 0.01
    val isAgentMatching = intent?.payload?.claimedAgentId == null || intent.payload.claimedAgentId == intent.payload.agentId
    val isNotExpired = (intent?.expiresInSeconds ?: 180) > 0
    val isNotReplay = intent?.payload?.scenarioTag != "replay_attack"
    val isNotForged = intent?.payload?.scenarioTag != "fake_request"

    val isMatching = isDestMatching && isAmountMatching && isAgentMatching && isNotExpired && isNotReplay && isNotForged
    val isHindi = viewModel.isRuralMode && viewModel.ruralLanguage == "hi"

    // Text To Speech initialization for Assisted Rural Mode
    val context = LocalContext.current
    var tts: TextToSpeech? by remember { mutableStateOf(null) }

    DisposableEffect(Unit) {
        var speech: TextToSpeech? = null
        speech = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                val locale = if (isHindi) Locale("hi", "IN") else Locale.US
                speech?.language = locale
            }
        }
        tts = speech
        onDispose {
            speech?.stop()
            speech?.shutdown()
        }
    }

    val ttsSpeechText = if (isHindi) {
        "TVS क्रेडिट ने आपके ऋण ${intent?.payload?.loanId ?: "4521"} के लिए $requestedAmount रुपये के भुगतान को अधिकृत किया है। अधिकृत खाता है $authorizedDestination"
    } else {
        "TVS Credit has authorized a payment of rupees $requestedAmount for loan ${intent?.payload?.loanId ?: "4521"}. Authorized recipient is $authorizedDestination"
    }

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
                    text = if (isHindi) "सटीक कार्रवाई द्वार" else "Exact Action Gate",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = TvsNavy
                )
                Text(
                    text = "TVS FINANCIAL-INTERACTION FIREWALL",
                    fontSize = 10.sp,
                    fontWeight = FontWeight.ExtraBold,
                    letterSpacing = 1.sp,
                    color = TvsGreenDark
                )
            }
        }

        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Text to Speech Readout Bar (Accessibility & Rural Mode)
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(14.dp))
                    .background(Color(0xFFE0F2FE))
                    .border(1.dp, Color(0xFFBAE6FD), RoundedCornerShape(14.dp))
                    .padding(14.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                IconButton(
                    onClick = {
                        tts?.speak(ttsSpeechText, TextToSpeech.QUEUE_FLUSH, null, "PRAMAAN_TTS")
                    },
                    modifier = Modifier
                        .size(40.dp)
                        .background(OrbBlue.copy(alpha = 0.2f), CircleShape)
                ) {
                    Icon(Icons.Filled.VolumeUp, contentDescription = "Voice Readout", tint = OrbBlue)
                }
                Spacer(Modifier.width(12.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        if (isHindi) "आवाज़ में सुनें (Voice Readout)" else "Listen to Authorized Intent",
                        color = TvsNavy,
                        fontSize = 13.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        if (isHindi) "TVS अधिकृत विवरण सुनें" else "Tap speaker to hear spoken cryptographic intent",
                        color = TextMuted,
                        fontSize = 11.sp
                    )
                }
            }

            // Customer Hero Verification Card (Glassmorphic White)
            GlassCard(
                borderColor = if (isMatching) Color(0xFF86EFAC) else Color(0xFFFECACA),
                glowColor = if (isMatching) Color(0x4000C853) else Color(0x40EF4444)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        if (isHindi) "अनुरोधित लेन-देन" else "REQUESTED TRANSACTION",
                        color = TextMuted,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        letterSpacing = 1.sp
                    )
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(20.dp))
                            .background(
                                if (!isMatching) Color(0xFFFEE2E2)
                                else if (requiresStepUp) Color(0xFFFEF3C7)
                                else Color(0xFFDCFCE7)
                            )
                            .border(
                                1.dp,
                                if (!isMatching) Color(0xFFFCA5A5)
                                else if (requiresStepUp) Color(0xFFFCD34D)
                                else Color(0xFF86EFAC),
                                RoundedCornerShape(20.dp)
                            )
                            .padding(horizontal = 10.dp, vertical = 4.dp)
                    ) {
                        Text(
                            text = if (!isMatching)
                                (if (isHindi) "अवरुद्ध" else "BLOCKED")
                            else if (requiresStepUp)
                                (if (isHindi) "अतिरिक्त सत्यापन आवश्यक" else "ADDITIONAL VERIFICATION REQUIRED")
                            else
                                (if (isHindi) "सत्यापित" else "VERIFIED"),
                            color = if (!isMatching) AlertRed
                            else if (requiresStepUp) Color(0xFFB45309)
                            else TvsGreenDark,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.ExtraBold,
                            letterSpacing = 0.6.sp
                        )
                    }
                }

                Spacer(Modifier.height(16.dp))

                Text(
                    text = requestedPurpose,
                    color = TextMuted,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 0.5.sp
                )
                Text(
                    text = "₹$requestedAmount",
                    color = TvsNavy,
                    fontSize = 36.sp,
                    fontWeight = FontWeight.ExtraBold
                )

                Spacer(Modifier.height(16.dp))

                // Authorized vs Claimed Destination Comparison
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(12.dp))
                        .background(Color(0xFFF8FAFC))
                        .border(1.dp, GlassBorderLight, RoundedCornerShape(12.dp))
                        .padding(14.dp)
                ) {
                    Column {
                        Text(
                            if (isHindi) "TVS द्वारा अधिकृत खाता:" else "TVS Authorized Account:",
                            color = TextMuted,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.SemiBold
                        )
                        Spacer(Modifier.height(2.dp))
                        Text(
                            authorizedDestination,
                            color = TvsGreenDark,
                            fontSize = 14.sp,
                            fontFamily = FontFamily.Monospace,
                            fontWeight = FontWeight.Bold
                        )

                        Spacer(Modifier.height(10.dp))

                        Text(
                            if (isHindi) "वर्तमान अनुरोधित खाता (Paying To):" else "Current Requested Destination:",
                            color = TextMuted,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.SemiBold
                        )
                        Spacer(Modifier.height(2.dp))
                        Text(
                            claimedDestination,
                            color = if (isMatching) TvsNavy else AlertRed,
                            fontSize = 14.sp,
                            fontFamily = FontFamily.Monospace,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }

                Spacer(Modifier.height(14.dp))

                // Trust Status Explanation
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(12.dp))
                        .background(
                            if (isMatching) Color(0xFFF0FDF4) else Color(0xFFFEF2F2)
                        )
                        .border(
                            1.dp,
                            if (isMatching) Color(0xFFBBF7D0) else Color(0xFFFECACA),
                            RoundedCornerShape(12.dp)
                        )
                        .padding(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        if (isMatching) Icons.Filled.CheckCircle else Icons.Filled.GppBad,
                        contentDescription = null,
                        tint = if (isMatching) TvsGreen else AlertRed,
                        modifier = Modifier.size(24.dp)
                    )
                    Spacer(Modifier.width(12.dp))
                    Column {
                        Text(
                            text = if (!isMatching)
                                (if (isHindi) "अवरुद्ध: बेमेल या अनधिकृत खाता" else "Blocked: Unverified Recipient")
                            else if (requiresStepUp)
                                (if (isHindi) "अतिरिक्त सत्यापन आवश्यक" else "Additional Verification Required")
                            else
                                (if (isHindi) "सत्यापित: सुरक्षित भुगतान" else "Verified: Safe to Proceed"),
                            color = if (!isMatching) AlertRed
                            else if (requiresStepUp) Color(0xFFB45309)
                            else TvsGreenDark,
                            fontSize = 13.sp,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = if (!isMatching)
                                (if (isHindi) "यह खाता TVS रिकॉर्ड से मेल नहीं खाता है। पैसे न भेजें।" else "This recipient does NOT match TVS records. Do not transfer money.")
                            else if (requiresStepUp)
                                (if (isHindi) "संवेदनशील लेन-देन संदर्भ: आगे बढ़ने के लिए आपकी स्पष्ट स्वीकृति आवश्यक है।" else "Contextual sensitivity elevated. Explicit confirmation required to proceed.")
                            else
                                (if (isHindi) "यह प्राप्तकर्ता आधिकारिक TVS खाते से मेल खाता है।" else "This recipient matches TVS Credit official collection account."),
                            color = if (!isMatching) Color(0xFF991B1B)
                            else if (requiresStepUp) Color(0xFF92400E)
                            else Color(0xFF166534),
                            fontSize = 11.sp,
                            lineHeight = 15.sp
                        )
                    }
                }
            }

            // Contextual Step-Up Confirmation Checkbox (Only shown when elevated contextual risk requires it)
            if (isMatching && requiresStepUp) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(12.dp))
                        .background(Color(0xFFFFFBEB))
                        .border(1.dp, Color(0xFFFDE68A), RoundedCornerShape(12.dp))
                        .padding(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Checkbox(
                        checked = highRiskConfirmed,
                        onCheckedChange = { highRiskConfirmed = it },
                        colors = CheckboxDefaults.colors(
                            checkedColor = TvsGreen,
                            checkmarkColor = Color.White,
                            uncheckedColor = TextMuted
                        )
                    )
                    Spacer(Modifier.width(6.dp))
                    Text(
                        if (isHindi)
                            "मैं पुष्टि करता हूँ कि मैंने ऋण खाता और प्राप्तकर्ता की पुष्टि कर ली है।"
                        else
                            "I confirm that I have verified the loan details and recipient account.",
                        fontSize = 12.sp,
                        color = TvsNavy
                    )
                }
            }

            if (intent == null) {
                GlassCard(
                    borderColor = Color(0xFFFDE68A),
                    glowColor = Color(0x30F59E0B)
                ) {
                    Text(
                        "⚠️ NO ACTIVE INTERACTION PENDING",
                        color = Color(0xFFD97706),
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        letterSpacing = 1.sp
                    )
                    Spacer(Modifier.height(6.dp))
                    Text(
                        "No contact interaction is currently active for this customer. Please initiate an interaction from the TVS Operations Console, or tap Reset/Refresh on Home.",
                        color = TextMuted,
                        fontSize = 12.sp,
                        lineHeight = 16.sp
                    )
                }
            }

            // Customer Action Buttons (Risk-proportional: streamlined 1-touch for routine, confirmed for step-up)
            PrimaryButton(
                text = if (intent == null) "Return to Home Dashboard"
                else if (!isMatching) (if (isHindi) "अवरुद्ध करें और रिपोर्ट करें" else "Block & Report Untrusted Request")
                else if (requiresStepUp) (if (isHindi) "अतिरिक्त सत्यापन के साथ अधिकृत करें" else "Confirm & Authorize with Step-Up")
                else (if (isHindi) "भुगतान अधिकृत करें" else "Authorize Payment"),
                containerColor = if (intent == null) TvsNavy
                else if (!isMatching) AlertRed
                else if (requiresStepUp && !highRiskConfirmed) Color(0xFF94A3B8)
                else TvsGreen,
                onClick = {
                    if (intent == null) {
                        navController.navigate("home") {
                            popUpTo("home") { inclusive = true }
                        }
                        return@PrimaryButton
                    }
                    if (isMatching && requiresStepUp && !highRiskConfirmed) {
                        return@PrimaryButton
                    }
                    val sendConfirmed = isMatching && requiresStepUp && highRiskConfirmed
                    viewModel.verifyExactAction(claimedDestination, deviceConfirmed = sendConfirmed) { isAllowed, isStepUp ->
                        viewModel.loadReceiptHistory()
                        if (isStepUp) {
                            requiresStepUp = true
                        } else if (isAllowed) {
                            navController.navigate("receipt") {
                                popUpTo("action_gate") { inclusive = true }
                            }
                        } else {
                            navController.navigate("blocked") {
                                popUpTo("action_gate") { inclusive = true }
                            }
                        }
                    }
                }
            )

            // Customer Kill Switch
            DangerButton(
                text = if (isHindi) "मुझे इस अनुरोध पर भरोसा नहीं है (किल स्विच)" else "I DON'T TRUST THIS REQUEST",
                enabled = intent != null,
                onClick = {
                    if (intent == null) return@DangerButton
                    viewModel.triggerKillSwitch {
                        viewModel.loadReceiptHistory()
                        navController.navigate("kill_switch_report") {
                            popUpTo("action_gate") { inclusive = true }
                        }
                    }
                }
            )

            // EXPANDABLE TECHNICAL VERIFICATION & ATTACK SIMULATION SECTION (Glassmorphic White)
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(16.dp))
                    .background(Color.White)
                    .border(1.dp, GlassBorderLight, RoundedCornerShape(16.dp))
                    .clickable { isTechnicalDetailsExpanded = !isTechnicalDetailsExpanded }
                    .padding(16.dp)
            ) {
                Column {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                Icons.Filled.Lock,
                                contentDescription = null,
                                tint = TvsGreen,
                                modifier = Modifier.size(18.dp)
                            )
                            Spacer(Modifier.width(8.dp))
                            Text(
                                "Cryptographic Proof & Attack Simulator",
                                color = TvsNavy,
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                        Icon(
                            imageVector = if (isTechnicalDetailsExpanded) Icons.Filled.ExpandLess else Icons.Filled.ExpandMore,
                            contentDescription = null,
                            tint = TextMuted
                        )
                    }

                    AnimatedVisibility(
                        visible = isTechnicalDetailsExpanded,
                        enter = fadeIn() + expandVertically(),
                        exit = fadeOut() + shrinkVertically()
                    ) {
                        Column(modifier = Modifier.padding(top = 16.dp)) {
                            Text(
                                "CRYPTOGRAPHIC INTENT PROOF",
                                color = TvsGreenDark,
                                fontSize = 10.sp,
                                fontWeight = FontWeight.ExtraBold,
                                letterSpacing = 1.sp
                            )
                            Spacer(Modifier.height(8.dp))
                            LabelValueRow("Algorithm", "Ed25519 • Asymmetric Digital Signature")
                            LabelValueRow("Intent Token ID", intent?.payload?.intentId ?: "INT-SIM-001", isMono = true)
                            LabelValueRow("Policy Version", "3.2.0 (Adaptive Zero-Trust)")
                            LabelValueRow("Authorized Destination", authorizedDestination, isMono = true, valueColor = TvsGreenDark)
                            LabelValueRow("Nonce Freshness", "Single-Use Nonce Bound")
                            LabelValueRow("Gate Enforcement", "Strict Exact-Action Gate")

                            Spacer(Modifier.height(16.dp))

                            Text(
                                "TEST LIVE ATTACK VECTORS",
                                color = OrbOrange,
                                fontSize = 10.sp,
                                fontWeight = FontWeight.ExtraBold,
                                letterSpacing = 1.sp
                            )
                            Spacer(Modifier.height(6.dp))
                            Text(
                                "Simulate destination tampering to verify the Exact Action Gate in real-time:",
                                color = TextMuted,
                                fontSize = 11.sp
                            )
                            Spacer(Modifier.height(10.dp))

                            OutlinedTextField(
                                value = claimedDestination,
                                onValueChange = { claimedDestination = it },
                                modifier = Modifier.fillMaxWidth(),
                                singleLine = true,
                                textStyle = MaterialTheme.typography.bodyMedium.copy(
                                    fontFamily = FontFamily.Monospace,
                                    fontWeight = FontWeight.SemiBold,
                                    color = TvsNavy
                                ),
                                label = { Text("Tested Recipient VPA", color = TextMuted) },
                                colors = OutlinedTextFieldDefaults.colors(
                                    focusedBorderColor = TvsGreen,
                                    unfocusedBorderColor = GlassBorderLight,
                                    focusedTextColor = TvsNavy,
                                    unfocusedTextColor = TvsNavy,
                                    cursorColor = TvsGreen
                                )
                            )

                            Spacer(Modifier.height(10.dp))

                            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                                Box(
                                    modifier = Modifier
                                        .clip(RoundedCornerShape(8.dp))
                                        .background(if (isMatching) Color(0xFFDCFCE7) else Color(0xFFF1F5F9))
                                        .border(1.dp, if (isMatching) Color(0xFF86EFAC) else GlassBorderLight, RoundedCornerShape(8.dp))
                                        .clickable { claimedDestination = authorizedDestination }
                                        .padding(horizontal = 12.dp, vertical = 7.dp)
                                ) {
                                    Text(
                                        "Genuine VPA",
                                        fontSize = 11.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = if (isMatching) TvsGreenDark else TextMuted
                                    )
                                }

                                Box(
                                    modifier = Modifier
                                        .clip(RoundedCornerShape(8.dp))
                                        .background(if (!isMatching) Color(0xFFFEE2E2) else Color(0xFFF1F5F9))
                                        .border(1.dp, if (!isMatching) Color(0xFFFCA5A5) else GlassBorderLight, RoundedCornerShape(8.dp))
                                        .clickable { claimedDestination = "fraudster123@upi" }
                                        .padding(horizontal = 12.dp, vertical = 7.dp)
                                ) {
                                    Text(
                                        "Rogue VPA (Tampered)",
                                        fontSize = 11.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = if (!isMatching) AlertRed else TextMuted
                                    )
                                }
                            }
                        }
                    }
                }
            }

            LoadingOverlay(viewModel.isLoading)
        }
    }
}
