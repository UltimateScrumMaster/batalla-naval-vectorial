using System;
using Godot;

namespace BatallaNavalVectorial.UI
{
    public partial class MainMenu : Control
    {
        private LineEdit _txtName = null!;
        private OptionButton _optTheme = null!;
        private HSlider _sliderVolume = null!;
        private Label _lblVolume = null!;
        private OptionButton _optAnimSpeed = null!;
        private CheckButton _chkAnimations = null!;
        private Button _btnStart = null!;
        private LineEdit _txtServerUri = null!;

        public override void _Ready()
        {
            SetupUI();
        }

        private void SetupUI()
        {
            var centerContainer = new CenterContainer
            {
                AnchorRight = 1.0f,
                AnchorBottom = 1.0f
            };
            AddChild(centerContainer);

            var panel = new PanelContainer
            {
                CustomMinimumSize = new Vector2(580, 620)
            };
            centerContainer.AddChild(panel);

            var margin = new MarginContainer();
            margin.AddThemeConstantOverride("margin_left", 30);
            margin.AddThemeConstantOverride("margin_right", 30);
            margin.AddThemeConstantOverride("margin_top", 25);
            margin.AddThemeConstantOverride("margin_bottom", 25);
            panel.AddChild(margin);

            var vBox = new VBoxContainer { CustomMinimumSize = new Vector2(520, 560) };
            vBox.AddThemeConstantOverride("separation", 14);
            margin.AddChild(vBox);

            // Título Principal
            var lblTitle = new Label
            {
                Text = "BATALLA NAVAL VECTORIAL",
                HorizontalAlignment = HorizontalAlignment.Center
            };
            lblTitle.AddThemeFontSizeOverride("font_size", 22);
            vBox.AddChild(lblTitle);

            var lblSubtitle = new Label
            {
                Text = "Simulación Táctica de Álgebra Lineal & Geometría Analítica",
                HorizontalAlignment = HorizontalAlignment.Center
            };
            lblSubtitle.AddThemeFontSizeOverride("font_size", 12);
            lblSubtitle.AddThemeColorOverride("font_color", new Color(0.4f, 0.8f, 1.0f));
            vBox.AddChild(lblSubtitle);

            vBox.AddChild(new HSeparator());

            // 1. Nombre del Comandante
            vBox.AddChild(new Label { Text = "Nombre del Comandante:" });
            _txtName = new LineEdit
            {
                Text = GameSettings.PlayerName,
                PlaceholderText = "Ingresa tu nombre o rango militar..."
            };
            _txtName.TextChanged += newText => GameSettings.PlayerName = string.IsNullOrWhiteSpace(newText) ? "Comandante" : newText;
            vBox.AddChild(_txtName);

            // 2. Aspecto Visual del Radar (Tema)
            vBox.AddChild(new Label { Text = "Aspecto Visual / Tema del Radar:" });
            _optTheme = new OptionButton();
            _optTheme.AddItem("Cyber-Navy (Azul Táctico & Cian)", 0);
            _optTheme.AddItem("Fósforo Verde (Radar CRT Militar)", 1);
            _optTheme.AddItem("Ámbar Alerta (Consola Sci-Fi Retro)", 2);
            _optTheme.Select((int)GameSettings.CurrentTheme);
            _optTheme.ItemSelected += index => GameSettings.CurrentTheme = (RadarTheme)index;
            vBox.AddChild(_optTheme);

            // 3. Servidor WebSocket
            vBox.AddChild(new Label { Text = "Servidor de Cálculo Matemático (Python WS):" });
            _txtServerUri = new LineEdit { Text = GameSettings.ServerUri };
            _txtServerUri.TextChanged += uri => GameSettings.ServerUri = uri;
            vBox.AddChild(_txtServerUri);

            // 4. Velocidad de Animación y Toggle
            var animRow = new HBoxContainer();
            vBox.AddChild(animRow);

            var vBoxSpeed = new VBoxContainer { SizeFlagsHorizontal = SizeFlags.ExpandFill };
            vBoxSpeed.AddChild(new Label { Text = "Velocidad de Animaciones:" });
            _optAnimSpeed = new OptionButton();
            _optAnimSpeed.AddItem("0.6x (Lenta / Didáctica)", 0);
            _optAnimSpeed.AddItem("1.0x (Normal)", 1);
            _optAnimSpeed.AddItem("1.6x (Táctica Rápida)", 2);
            _optAnimSpeed.AddItem("2.5x (Ultra Rápida)", 3);
            _optAnimSpeed.Select(1);
            _optAnimSpeed.ItemSelected += index => GameSettings.AnimationSpeed = index switch
            {
                0 => 0.6f,
                1 => 1.0f,
                2 => 1.6f,
                3 => 2.5f,
                _ => 1.0f
            };
            vBoxSpeed.AddChild(_optAnimSpeed);
            animRow.AddChild(vBoxSpeed);

            _chkAnimations = new CheckButton
            {
                Text = "Animaciones Activas",
                ButtonPressed = GameSettings.EnableAnimations
            };
            _chkAnimations.Toggled += toggled => GameSettings.EnableAnimations = toggled;
            animRow.AddChild(_chkAnimations);

            // 5. Volumen Master
            var volRow = new HBoxContainer();
            volRow.AddChild(new Label { Text = "Volumen de Efectos: " });
            _lblVolume = new Label { Text = $"{(int)(GameSettings.MasterVolume * 100)}%" };
            volRow.AddChild(_lblVolume);
            vBox.AddChild(volRow);

            _sliderVolume = new HSlider
            {
                MinValue = 0,
                MaxValue = 100,
                Value = (int)(GameSettings.MasterVolume * 100)
            };
            _sliderVolume.ValueChanged += val =>
            {
                GameSettings.MasterVolume = (float)val / 100.0f;
                _lblVolume.Text = $"{(int)val}%";
            };
            vBox.AddChild(_sliderVolume);

            vBox.AddChild(new HSeparator());

            // Botón de Inicio
            _btnStart = new Button
            {
                Text = "[ INICIAR BATALLA NAVAL (VS IA) ]",
                CustomMinimumSize = new Vector2(0, 52)
            };
            _btnStart.AddThemeFontSizeOverride("font_size", 15);
            _btnStart.Pressed += OnStartPressed;
            vBox.AddChild(_btnStart);
        }

        private void OnStartPressed()
        {
            GetTree().ChangeSceneToFile("res://Scenes/Battle.tscn");
        }
    }
}
