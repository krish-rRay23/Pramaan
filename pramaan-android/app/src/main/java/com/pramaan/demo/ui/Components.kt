package com.pramaan.demo.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pramaan.demo.ui.theme.AlertRed
import com.pramaan.demo.ui.theme.GlassBorderLight
import com.pramaan.demo.ui.theme.GlassBorderMint
import com.pramaan.demo.ui.theme.GlassFillWhite
import com.pramaan.demo.ui.theme.TextMint
import com.pramaan.demo.ui.theme.TextMuted
import com.pramaan.demo.ui.theme.TextPrimary
import com.pramaan.demo.ui.theme.TextWhite
import com.pramaan.demo.ui.theme.TvsGreen
import com.pramaan.demo.ui.theme.TvsGreenDark
import com.pramaan.demo.ui.theme.TvsNavy

@Composable
fun GlassCard(
    modifier: Modifier = Modifier,
    backgroundColor: Color = GlassFillWhite,
    borderColor: Color = GlassBorderLight,
    glowColor: Color = GlassBorderMint,
    cornerRadius: Int = 20,
    content: @Composable ColumnScope.() -> Unit,
) {
    val shape = RoundedCornerShape(cornerRadius.dp)
    Column(
        modifier = modifier
            .fillMaxWidth()
            .shadow(
                elevation = 6.dp,
                shape = shape,
                ambientColor = Color(0x0A000000),
                spotColor = Color(0x140A192F)
            )
            .clip(shape)
            .background(
                Brush.verticalGradient(
                    colors = listOf(
                        backgroundColor,
                        backgroundColor.copy(alpha = 0.94f)
                    )
                )
            )
            .border(
                width = 1.dp,
                brush = Brush.verticalGradient(
                    colors = listOf(
                        glowColor.copy(alpha = 0.5f),
                        borderColor
                    )
                ),
                shape = shape
            )
            .padding(20.dp),
        content = content,
    )
}

@Composable
fun SectionCard(
    modifier: Modifier = Modifier,
    backgroundColor: Color = GlassFillWhite,
    borderColor: Color = GlassBorderLight,
    content: @Composable ColumnScope.() -> Unit,
) {
    GlassCard(
        modifier = modifier,
        backgroundColor = backgroundColor,
        borderColor = borderColor,
        content = content,
    )
}

@Composable
fun LabelValueRow(
    label: String,
    value: String,
    valueColor: Color = TextPrimary,
    isMono: Boolean = false
) {
    if (value.length > 18) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 4.dp)
        ) {
            Text(
                text = label,
                color = TextMuted,
                style = MaterialTheme.typography.bodyMedium,
                fontSize = 12.sp,
            )
            Spacer(Modifier.height(3.dp))
            Text(
                text = value,
                color = valueColor,
                style = MaterialTheme.typography.titleMedium,
                fontSize = 12.sp,
                fontFamily = if (isMono) FontFamily.Monospace else FontFamily.Default,
                fontWeight = if (isMono) FontWeight.SemiBold else FontWeight.Bold,
            )
        }
    } else {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 5.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            Text(
                text = label,
                color = TextMuted,
                style = MaterialTheme.typography.bodyMedium,
                fontSize = 13.sp,
                modifier = Modifier.weight(1f, fill = false),
            )
            Spacer(Modifier.width(8.dp))
            Text(
                text = value,
                color = valueColor,
                style = MaterialTheme.typography.titleMedium,
                fontSize = 13.sp,
                fontFamily = if (isMono) FontFamily.Monospace else FontFamily.Default,
                fontWeight = if (isMono) FontWeight.SemiBold else FontWeight.Bold,
                textAlign = TextAlign.End,
            )
        }
    }
}

@Composable
fun SecurityStatusBadge(
    status: String = "FIREWALL ACTIVE",
    color: Color = TvsGreenDark,
) {
    Row(
        modifier = Modifier
            .clip(RoundedCornerShape(24.dp))
            .background(Color(0xFFDCFCE7))
            .border(1.dp, Color(0xFF86EFAC), RoundedCornerShape(24.dp))
            .padding(horizontal = 12.dp, vertical = 5.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(
            modifier = Modifier
                .size(7.dp)
                .background(color, CircleShape)
        )
        Spacer(Modifier.width(6.dp))
        Text(
            text = status,
            color = color,
            fontSize = 11.sp,
            fontWeight = FontWeight.ExtraBold,
            letterSpacing = 0.8.sp,
        )
    }
}

@Composable
fun GlassChip(
    text: String,
    color: Color = TvsGreenDark,
    modifier: Modifier = Modifier,
) {
    Text(
        text = text,
        color = color,
        fontSize = 11.sp,
        fontWeight = FontWeight.Bold,
        letterSpacing = 0.5.sp,
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .background(color.copy(alpha = 0.1f))
            .border(0.5.dp, color.copy(alpha = 0.35f), RoundedCornerShape(8.dp))
            .padding(horizontal = 8.dp, vertical = 3.dp)
    )
}

@Composable
fun PrimaryButton(
    text: String,
    enabled: Boolean = true,
    containerColor: Color = TvsGreen,
    contentColor: Color = Color.White,
    onClick: () -> Unit,
) {
    Button(
        onClick = onClick,
        enabled = enabled,
        modifier = Modifier
            .fillMaxWidth()
            .height(54.dp)
            .shadow(8.dp, RoundedCornerShape(16.dp), ambientColor = TvsGreen.copy(alpha = 0.25f), spotColor = TvsGreen.copy(alpha = 0.35f)),
        colors = ButtonDefaults.buttonColors(
            containerColor = containerColor,
            contentColor = contentColor,
            disabledContainerColor = Color(0xFFE2E8F0),
            disabledContentColor = TextMuted
        ),
        shape = RoundedCornerShape(16.dp),
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            letterSpacing = 0.4.sp
        )
    }
}

@Composable
fun DangerButton(
    text: String,
    enabled: Boolean = true,
    onClick: () -> Unit,
) {
    Button(
        onClick = onClick,
        enabled = enabled,
        modifier = Modifier
            .fillMaxWidth()
            .height(54.dp)
            .shadow(8.dp, RoundedCornerShape(16.dp), ambientColor = AlertRed.copy(alpha = 0.25f), spotColor = AlertRed.copy(alpha = 0.35f)),
        colors = ButtonDefaults.buttonColors(
            containerColor = AlertRed,
            contentColor = Color.White
        ),
        shape = RoundedCornerShape(16.dp),
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            letterSpacing = 0.4.sp
        )
    }
}

@Composable
fun SecondaryButton(
    text: String,
    enabled: Boolean = true,
    onClick: () -> Unit
) {
    OutlinedButton(
        onClick = onClick,
        enabled = enabled,
        modifier = Modifier
            .fillMaxWidth()
            .height(52.dp)
            .shadow(2.dp, RoundedCornerShape(16.dp), ambientColor = Color(0x08000000)),
        colors = ButtonDefaults.outlinedButtonColors(
            containerColor = Color.White,
            contentColor = TextPrimary
        ),
        border = androidx.compose.foundation.BorderStroke(1.dp, GlassBorderLight),
        shape = RoundedCornerShape(16.dp),
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.titleMedium,
            color = TextPrimary,
            fontWeight = FontWeight.Bold
        )
    }
}

@Composable
fun LoadingOverlay(visible: Boolean) {
    if (visible) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),
            contentAlignment = Alignment.Center,
        ) {
            CircularProgressIndicator(
                color = TvsGreen,
                strokeWidth = 3.dp,
                modifier = Modifier.size(36.dp)
            )
        }
    }
}

@Composable
fun ErrorBanner(message: String?, onDismiss: () -> Unit) {
    if (message != null) {
        GlassCard(
            backgroundColor = Color(0xFFFEF2F2),
            borderColor = Color(0xFFFECACA),
            glowColor = Color(0xFFFCA5A5)
        ) {
            Text(
                message,
                color = Color(0xFF991B1B),
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.SemiBold
            )
            Spacer(Modifier.height(8.dp))
            OutlinedButton(
                onClick = onDismiss,
                border = androidx.compose.foundation.BorderStroke(1.dp, Color(0xFFF87171)),
                colors = ButtonDefaults.outlinedButtonColors(contentColor = Color(0xFF991B1B))
            ) {
                Text("Dismiss", color = Color(0xFF991B1B), fontSize = 12.sp)
            }
        }
    }
}
