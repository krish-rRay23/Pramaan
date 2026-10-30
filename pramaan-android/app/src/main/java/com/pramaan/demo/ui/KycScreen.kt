package com.pramaan.demo.ui

import android.content.Context
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
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
import androidx.compose.material.icons.filled.Fingerprint
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Security
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import coil.compose.AsyncImage
import com.pramaan.demo.PramaanViewModel
import com.pramaan.demo.ui.theme.AlertRed
import com.pramaan.demo.ui.theme.CanvasGlowMid
import com.pramaan.demo.ui.theme.CanvasGlowTop
import com.pramaan.demo.ui.theme.CanvasLightBg
import com.pramaan.demo.ui.theme.CanvasWhite
import com.pramaan.demo.ui.theme.GlassBorderLight
import com.pramaan.demo.ui.theme.OrbBlue
import com.pramaan.demo.ui.theme.TextMint
import com.pramaan.demo.ui.theme.TextMuted
import com.pramaan.demo.ui.theme.TextPrimary
import com.pramaan.demo.ui.theme.TextWhite
import com.pramaan.demo.ui.theme.TvsGreen
import com.pramaan.demo.ui.theme.TvsGreenDark
import com.pramaan.demo.ui.theme.TvsNavy
import java.io.File
import java.io.FileOutputStream

private fun uriToTempFile(context: Context, uri: Uri): File? {
    return try {
        val inputStream = context.contentResolver.openInputStream(uri) ?: return null
        val tempFile = File(context.cacheDir, "kyc_upload_${System.currentTimeMillis()}.jpg")
        FileOutputStream(tempFile).use { output -> inputStream.copyTo(output) }
        inputStream.close()
        tempFile
    } catch (e: Exception) {
        null
    }
}

@Composable
fun KycScreen(navController: NavHostController, viewModel: PramaanViewModel = viewModel()) {
    val context = LocalContext.current
    var pickedUri by remember { mutableStateOf<Uri?>(null) }
    var isAboutExpanded by remember { mutableStateOf(false) }

    val pickImage = rememberLauncherForActivityResult(ActivityResultContracts.GetContent()) { uri ->
        pickedUri = uri
    }

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
                    text = "Identity & Document Protection",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = TvsNavy
                )
                Text(
                    text = "MEDIA & KYC AUTHENTICITY SHIELD",
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
            // Customer Overview Card (GlassCard White)
            GlassCard {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(44.dp)
                            .clip(CircleShape)
                            .background(Color(0xFFE0F2FE))
                            .border(1.dp, Color(0xFFBAE6FD), CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            Icons.Filled.Fingerprint,
                            contentDescription = null,
                            tint = OrbBlue,
                            modifier = Modifier.size(26.dp)
                        )
                    }
                    Spacer(Modifier.width(14.dp))
                    Column {
                        Text(
                            "Identity Authenticity Check",
                            fontWeight = FontWeight.Bold,
                            color = TvsNavy,
                            fontSize = 14.sp
                        )
                        Text(
                            "TVS Credit Media & KYC Authenticity Check",
                            color = TvsGreenDark,
                            fontSize = 11.sp
                        )
                    }
                }
                Spacer(Modifier.height(12.dp))
                Text(
                    "Upload a government ID card or customer selfie to verify image authenticity and protect your account against identity tampering and digital deepfakes.",
                    color = TextMuted,
                    fontSize = 12.sp,
                    lineHeight = 17.sp
                )
            }

            SecondaryButton("Select Photo / Document") { pickImage.launch("image/*") }

            pickedUri?.let { uri ->
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(16.dp))
                        .border(1.dp, GlassBorderLight, RoundedCornerShape(16.dp))
                ) {
                    AsyncImage(
                        model = uri,
                        contentDescription = "Selected photo",
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(220.dp)
                            .clip(RoundedCornerShape(16.dp)),
                    )
                }
            }

            ErrorBanner(viewModel.errorMessage, onDismiss = { viewModel.clearError() })

            PrimaryButton(
                text = "Verify Photo Authenticity",
                enabled = pickedUri != null,
                containerColor = TvsGreen,
                onClick = {
                    pickedUri?.let { uri ->
                        uriToTempFile(context, uri)?.let { file -> viewModel.submitKycImage(file) }
                    }
                }
            )

            // Analysis Result (GlassCard White)
            viewModel.authenticityResult?.let { result ->
                val isAuthentic = result.verdict == "authentic"
                val color = if (isAuthentic) TvsGreen else AlertRed
                GlassCard(
                    borderColor = if (isAuthentic) Color(0xFF86EFAC) else Color(0xFFFECACA),
                    glowColor = if (isAuthentic) Color(0x3300C853) else Color(0x33EF4444)
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = if (isAuthentic) Icons.Filled.CheckCircle else Icons.Filled.Security,
                            contentDescription = null,
                            tint = color,
                            modifier = Modifier.size(24.dp)
                        )
                        Spacer(Modifier.width(12.dp))
                        Column {
                            Text(
                                text = if (isAuthentic) "Identity Verification Passed" else "Review Recommended",
                                color = if (isAuthentic) TvsGreenDark else AlertRed,
                                fontSize = 14.sp,
                                fontWeight = FontWeight.ExtraBold
                            )
                            Text(
                                text = if (isAuthentic) "Photo authenticity confirmed with high confidence" else "Possible synthetic artifacts detected",
                                color = TextMuted,
                                fontSize = 11.sp
                            )
                        }
                    }

                    Spacer(Modifier.height(14.dp))
                    LabelValueRow(
                        "Risk Score",
                        "${(result.riskScore * 100).toInt()} / 100",
                        valueColor = if (isAuthentic) TvsGreenDark else AlertRed
                    )
                    LabelValueRow(
                        "Safety Status",
                        if (isAuthentic) "SAFE" else "FLAGGED",
                        valueColor = if (isAuthentic) TvsGreenDark else AlertRed
                    )
                    Spacer(Modifier.height(8.dp))
                    Text(result.note, style = MaterialTheme.typography.bodySmall, color = TextMuted)
                }
            }

            // EXPANDABLE "ABOUT THIS PROTECTION"
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(16.dp))
                    .background(Color.White)
                    .border(1.dp, GlassBorderLight, RoundedCornerShape(16.dp))
                    .clickable { isAboutExpanded = !isAboutExpanded }
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
                                Icons.Filled.Info,
                                contentDescription = null,
                                tint = OrbBlue,
                                modifier = Modifier.size(18.dp)
                            )
                            Spacer(Modifier.width(8.dp))
                            Text(
                                "About this Protection & Research Model",
                                color = TvsNavy,
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                        Icon(
                            imageVector = if (isAboutExpanded) Icons.Filled.ExpandLess else Icons.Filled.ExpandMore,
                            contentDescription = null,
                            tint = TextMuted
                        )
                    }

                    AnimatedVisibility(
                        visible = isAboutExpanded,
                        enter = fadeIn() + expandVertically(),
                        exit = fadeOut() + shrinkVertically()
                    ) {
                        Column(modifier = Modifier.padding(top = 14.dp)) {
                            Text(
                                "MODEL SPECIFICATION & ADAPTER ARCHITECTURE",
                                color = TvsGreenDark,
                                fontSize = 10.sp,
                                fontWeight = FontWeight.ExtraBold,
                                letterSpacing = 1.sp
                            )
                            Spacer(Modifier.height(8.dp))
                            LabelValueRow("Adapter Source", "prithivMLmods/open-deepfake-detection", isMono = true)
                            LabelValueRow("License", "Apache-2.0 Open Source")
                            LabelValueRow("Analysis Method", "Spatial Laplacian Edge Variance & Face ROI")
                            Spacer(Modifier.height(10.dp))
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clip(RoundedCornerShape(10.dp))
                                    .background(Color(0xFFF8FAFC))
                                    .border(1.dp, GlassBorderLight, RoundedCornerShape(10.dp))
                                    .padding(12.dp)
                            ) {
                                Text(
                                    "Prototype Disclosure: Powered by open-source research model (prithivMLmods/open-deepfake-detection). " +
                                    "Intended strictly as an illustrative open-source prototype / research model, not production-grade detection.",
                                    color = TextMuted,
                                    fontSize = 11.sp,
                                    lineHeight = 15.sp
                                )
                            }
                        }
                    }
                }
            }

            LoadingOverlay(viewModel.isLoading)
            Spacer(Modifier.height(16.dp))
        }
    }
}
