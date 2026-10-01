using System;
using Godot;

namespace BatallaNavalVectorial
{
    public enum RadarTheme
    {
        CyberNavy,     // Azul marino táctico y cian eléctrico
        MilitaryGreen, // Fósforo verde CRT retro
        AmberAlert     // Ámbar táctico militar
    }

    public static class GameSettings
    {
        public static string PlayerName { get; set; } = "Comandante";
        public static RadarTheme CurrentTheme { get; set; } = RadarTheme.CyberNavy;
        public static float MasterVolume { get; set; } = 0.8f;
        public static float AnimationSpeed { get; set; } = 1.0f; // 1.0 = Normal, 1.5 = Rápida, 2.0 = Muy Rápida
        public static bool EnableAnimations { get; set; } = true;
        public static string ServerUri { get; set; } = "ws://127.0.0.1:8765";

        public static Color GetThemeColorBackground() => CurrentTheme switch
        {
            RadarTheme.MilitaryGreen => new Color(0.02f, 0.08f, 0.04f, 0.95f),
            RadarTheme.AmberAlert => new Color(0.09f, 0.05f, 0.02f, 0.95f),
            _ => new Color(0.05f, 0.09f, 0.15f, 0.95f) // CyberNavy
        };

        public static Color GetThemeColorGrid() => CurrentTheme switch
        {
            RadarTheme.MilitaryGreen => new Color(0.1f, 0.35f, 0.15f, 0.8f),
            RadarTheme.AmberAlert => new Color(0.38f, 0.22f, 0.08f, 0.8f),
            _ => new Color(0.12f, 0.25f, 0.38f, 0.8f)
        };

        public static Color GetThemeColorPrimary() => CurrentTheme switch
        {
            RadarTheme.MilitaryGreen => new Color(0.2f, 0.95f, 0.3f, 1.0f),
            RadarTheme.AmberAlert => new Color(1.0f, 0.75f, 0.1f, 1.0f),
            _ => new Color(0.0f, 0.96f, 0.83f, 1.0f) // Cyan
        };

        public static Color GetThemeColorAccent() => CurrentTheme switch
        {
            RadarTheme.MilitaryGreen => new Color(0.6f, 1.0f, 0.4f, 1.0f),
            RadarTheme.AmberAlert => new Color(1.0f, 0.45f, 0.1f, 1.0f),
            _ => new Color(0.35f, 0.65f, 0.95f, 1.0f)
        };
    }
}
