package com.pramaan.demo.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val EpicWhiteGlassColorScheme = lightColorScheme(
    primary = TvsGreen,
    onPrimary = Color.White,
    primaryContainer = CanvasGlowTop,
    onPrimaryContainer = TvsGreenDark,
    secondary = OrbBlue,
    onSecondary = Color.White,
    tertiary = OrbOrange,
    onTertiary = Color.White,
    background = CanvasWhite,
    onBackground = TextPrimary,
    surface = GlassFillWhite,
    onSurface = TextPrimary,
    surfaceVariant = CanvasLightBg,
    onSurfaceVariant = TextSecondary,
    error = AlertRed,
    onError = Color.White,
)

@Composable
fun PramaanTheme(
    darkTheme: Boolean = false,
    content: @Composable () -> Unit,
) {
    MaterialTheme(
        colorScheme = EpicWhiteGlassColorScheme,
        typography = PramaanTypography,
        content = content,
    )
}
