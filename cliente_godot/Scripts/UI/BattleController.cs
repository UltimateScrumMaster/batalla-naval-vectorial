using System;
using System.Collections.Generic;
using System.Text.Json;
using System.Threading.Tasks;
using BatallaNavalVectorial.Network;
using BatallaNavalVectorial.Network.Protocol;
using Godot;

namespace BatallaNavalVectorial.UI
{
	public partial class BattleController : Control
	{
		private WebSocketClient _wsClient = null!;
		private RadarBoard _playerRadar = null!;
		private RadarBoard _enemyRadar = null!;
		private VectorAimOverlay _aimOverlay = null!;
		private MathConsole _mathConsole = null!;

		// HUD Controls
		private Label _lblStatus = null!;
		private Label _lblPlayerName = null!;
		private Label _lblEnergy = null!;
		private Label _lblWind = null!;
		private Label _lblTurn = null!;
		private OptionButton _optSkills = null!;
		private OptionButton _optShips = null!;

		// Containers para mostrar/ocultar según la habilidad
		private VBoxContainer _boxVectorV = null!;
		private VBoxContainer _boxVectorU = null!;
		private VBoxContainer _boxScalarK = null!;

		private HSlider _sliderVx = null!;
		private HSlider _sliderVy = null!;
		private HSlider _sliderUx = null!;
		private HSlider _sliderUy = null!;
		private HSlider _sliderK = null!;

		private Label _lblVx = null!;
		private Label _lblVy = null!;
		private Label _lblUx = null!;
		private Label _lblUy = null!;
		private Label _lblK = null!;

		private Button _btnFire = null!;
		private Button _btnBack = null!;

		private SessionReadyPayload? _sessionData;
		private Vector2I _selectedOrigin = Vector2I.Zero;
		private Vector2I _predictedImpact = Vector2I.Zero;
		private string _selectedSkill = "suma";
		private bool _isTurnInProgress = false;

		public override void _Ready()
		{
			SetupUI();
			SetupNetworking();
			AutoConnectAndStartGame();
		}

		private void SetupUI()
		{
			var mainLayout = new HBoxContainer
			{
				AnchorRight = 1.0f,
				AnchorBottom = 1.0f,
				OffsetLeft = 20,
				OffsetTop = 15,
				OffsetRight = -20,
				OffsetBottom = -15
			};
			AddChild(mainLayout);

			// 1. Columna Izquierda: Tableros
			var boardColumn = new VBoxContainer { CustomMinimumSize = new Vector2(740, 680) };
			mainLayout.AddChild(boardColumn);

			// Barra Superior de Estado
			var topBar = new HBoxContainer();
			_btnBack = new Button { Text = "◀ Menú Principal" };
			_btnBack.Pressed += () => GetTree().ChangeSceneToFile("res://Scenes/MainMenu.tscn");
			topBar.AddChild(_btnBack);

			_lblPlayerName = new Label
			{
				Text = $"[ {GameSettings.PlayerName.ToUpper()} ]",
				CustomMinimumSize = new Vector2(160, 30)
			};
			_lblPlayerName.AddThemeColorOverride("font_color", GameSettings.GetThemeColorPrimary());
			topBar.AddChild(_lblPlayerName);

			_lblStatus = new Label { Text = "ESTADO: INICIANDO...", CustomMinimumSize = new Vector2(160, 30) };
			_lblTurn = new Label { Text = "TURNO: 1", CustomMinimumSize = new Vector2(90, 30) };
			_lblEnergy = new Label { Text = "ENERGIA: 2/6 E", CustomMinimumSize = new Vector2(130, 30) };
			_lblWind = new Label { Text = "VIENTO: (0, 0)", CustomMinimumSize = new Vector2(130, 30) };

			topBar.AddChild(_lblStatus);
			topBar.AddChild(_lblTurn);
			topBar.AddChild(_lblEnergy);
			topBar.AddChild(_lblWind);
			boardColumn.AddChild(topBar);

			// Tableros Lado a Lado
			var boardsRow = new HBoxContainer();
			boardColumn.AddChild(boardsRow);

			_playerRadar = new RadarBoard { Title = "TU FLOTA (Plano Aliado)", IsEnemyRadar = false };
			_playerRadar.CellClicked += OnPlayerCellClicked;
			boardsRow.AddChild(_playerRadar);

			_enemyRadar = new RadarBoard { Title = "RADAR ENEMIGO (Niebla de Guerra)", IsEnemyRadar = true };
			_aimOverlay = new VectorAimOverlay { MouseFilter = MouseFilterEnum.Ignore };
			_enemyRadar.AddChild(_aimOverlay);
			boardsRow.AddChild(_enemyRadar);

			// Consola Matemática Pedagógica
			_mathConsole = new MathConsole { CustomMinimumSize = new Vector2(720, 200) };
			boardColumn.AddChild(_mathConsole);

			// 2. Columna Derecha: Panel de Mando Táctico
			var controlColumn = new VBoxContainer { CustomMinimumSize = new Vector2(480, 680) };
			controlColumn.AddThemeConstantOverride("separation", 8);
			mainLayout.AddChild(controlColumn);

			var lblHeader = new Label
			{
				Text = "CENTRO DE MANDO VECTORIAL",
				HorizontalAlignment = HorizontalAlignment.Center
			};
			lblHeader.AddThemeFontSizeOverride("font_size", 16);
			lblHeader.AddThemeColorOverride("font_color", GameSettings.GetThemeColorPrimary());
			controlColumn.AddChild(lblHeader);

			// Selector de Buque Emisor
			controlColumn.AddChild(new Label { Text = "1. Buque Emisor (Posición de Origen P):" });
			_optShips = new OptionButton();
			_optShips.ItemSelected += OnShipSelected;
			controlColumn.AddChild(_optShips);

			// Selector de Habilidad
			controlColumn.AddChild(new Label { Text = "2. Habilidad Táctica / Operación Vectorial:" });
			_optSkills = new OptionButton();
			_optSkills.AddItem("1. Disparo Simple (P + V) [0 E]", 0);
			_optSkills.AddItem("2. Artillería con Viento (P + V + W) [1 E]", 1);
			_optSkills.AddItem("3. Torpedo Escalar (P + k·U) [2 E]", 2);
			_optSkills.AddItem("4. Sónar de Gauss (Pitágoras) [1 E]", 3);
			_optSkills.AddItem("5. Cañón Orbital (proj_U(V)) [4 E]", 4);
			_optSkills.ItemSelected += OnSkillSelected;
			controlColumn.AddChild(_optSkills);

			// Contenedor para Vector V (Suma, Viento, Orbital)
			_boxVectorV = new VBoxContainer();
			_boxVectorV.AddChild(new Label { Text = "3. Vector de Disparo / Ataque V:" });
			_lblVx = new Label { Text = "Vx: 0" };
			_sliderVx = CreateSlider(-9, 9, 0, val => { _lblVx.Text = $"Vx: {val}"; RequestPreview(); });
			_boxVectorV.AddChild(_lblVx);
			_boxVectorV.AddChild(_sliderVx);

			_lblVy = new Label { Text = "Vy: 0" };
			_sliderVy = CreateSlider(-9, 9, 0, val => { _lblVy.Text = $"Vy: {val}"; RequestPreview(); });
			_boxVectorV.AddChild(_lblVy);
			_boxVectorV.AddChild(_sliderVy);
			controlColumn.AddChild(_boxVectorV);

			// Contenedor para Vector U (Torpedo y Orbital)
			_boxVectorU = new VBoxContainer();
			_boxVectorU.AddChild(new Label { Text = "4. Vector Base U (Dirección Torpedo / Eje Orbital):" });
			_lblUx = new Label { Text = "Ux: 1" };
			_sliderUx = CreateSlider(-9, 9, 1, val => { _lblUx.Text = $"Ux: {val}"; RequestPreview(); });
			_boxVectorU.AddChild(_lblUx);
			_boxVectorU.AddChild(_sliderUx);

			_lblUy = new Label { Text = "Uy: 0" };
			_sliderUy = CreateSlider(-9, 9, 0, val => { _lblUy.Text = $"Uy: {val}"; RequestPreview(); });
			_boxVectorU.AddChild(_lblUy);
			_boxVectorU.AddChild(_sliderUy);
			controlColumn.AddChild(_boxVectorU);

			// Contenedor para Escalar K (solo Torpedo)
			_boxScalarK = new VBoxContainer();
			_lblK = new Label { Text = "Potencia Escalar k (Multiplicador): 1" };
			_sliderK = CreateSlider(1, 5, 1, val => { _lblK.Text = $"Potencia Escalar k: {val}"; RequestPreview(); });
			_boxScalarK.AddChild(_lblK);
			_boxScalarK.AddChild(_sliderK);
			controlColumn.AddChild(_boxScalarK);

			// Ajustar visibilidad inicial para "suma"
			ActualizarVisibilidadSliders();

			// Botón de Disparo
			_btnFire = new Button
			{
				Text = "[ EJECUTAR DISPARO VECTORIAL ]",
				CustomMinimumSize = new Vector2(0, 48)
			};
			_btnFire.Pressed += OnFirePressed;
			controlColumn.AddChild(_btnFire);
		}

		private void ActualizarVisibilidadSliders()
		{
			switch (_selectedSkill)
			{
				case "suma":
				case "viento":
					_boxVectorV.Visible = true;
					_boxVectorU.Visible = false;
					_boxScalarK.Visible = false;
					break;
				case "torpedo":
					_boxVectorV.Visible = false;
					_boxVectorU.Visible = true;
					_boxScalarK.Visible = true;
					break;
				case "sonar":
					_boxVectorV.Visible = false;
					_boxVectorU.Visible = false;
					_boxScalarK.Visible = false;
					break;
				case "orbital":
					_boxVectorV.Visible = true;
					_boxVectorU.Visible = true;
					_boxScalarK.Visible = false;
					break;
			}
		}

		private HSlider CreateSlider(int min, int max, int defaultVal, Action<int> onChanged)
		{
			var slider = new HSlider
			{
				MinValue = min,
				MaxValue = max,
				Step = 1,
				Value = defaultVal,
				CustomMinimumSize = new Vector2(400, 20)
			};
			slider.ValueChanged += val => onChanged((int)val);
			return slider;
		}

		private void SetupNetworking()
		{
			_wsClient = new WebSocketClient();
			AddChild(_wsClient);

			_wsClient.Connected += OnConnected;
			_wsClient.Disconnected += OnDisconnected;
			_wsClient.SessionReady += OnSessionReady;
			_wsClient.PreviewReceived += OnPreviewReceived;
			_wsClient.TurnResolved += OnTurnResolved;
			_wsClient.ErrorReceived += OnErrorReceived;
		}

		private async void AutoConnectAndStartGame()
		{
			_lblStatus.Text = "ESTADO: CONECTANDO...";
			await _wsClient.ConnectToServerAsync(GameSettings.ServerUri);
			if (_wsClient.IsConnected)
			{
				await _wsClient.StartGameAsync();
			}
		}

		private void OnConnected()
		{
			_lblStatus.Text = "ESTADO: ONLINE [OK]";
			_mathConsole.AppendSuccess($"Servidor Python conectado. Bienvenido, {GameSettings.PlayerName}.");
		}

		private void OnDisconnected()
		{
			_lblStatus.Text = "ESTADO: DESCONECTADO [OFFLINE]";
			_mathConsole.AppendError("Conexión perdida con el servidor WebSocket.");
		}

		private void OnSessionReady(string json)
		{
			_sessionData = JsonSerializer.Deserialize<SessionReadyPayload>(json);
			if (_sessionData == null) return;

			UpdateGameStateUI();
			_mathConsole.AppendHeader("NUEVA CAMPAÑA TÁCTICA INICIADA");
			_mathConsole.AppendInfo($"Flota posicionada. Energía inicial: {_sessionData.Energia}/6. Viento actual: ({_sessionData.Viento[0]}, {_sessionData.Viento[1]})");
		}

		private void UpdateGameStateUI()
		{
			if (_sessionData == null) return;

			_lblTurn.Text = $"TURNO: {_sessionData.Turno}";
			_lblEnergy.Text = $"ENERGIA: {_sessionData.Energia}/{_sessionData.EnergiaMax} E";
			_lblWind.Text = $"VIENTO: ({_sessionData.Viento[0]}, {_sessionData.Viento[1]})";

			_playerRadar.UpdateBoard(_sessionData.TableroJugador);
			_enemyRadar.UpdateBoard(_sessionData.TableroEnemigo);

			_optShips.Clear();
			for (int i = 0; i < _sessionData.EmisoresDisponibles.Count; i++)
			{
				var em = _sessionData.EmisoresDisponibles[i];
				_optShips.AddItem($"{em.Barco} en ({em.Pos[0]}, {em.Pos[1]})", i);
			}

			if (_sessionData.EmisoresDisponibles.Count > 0)
			{
				var first = _sessionData.EmisoresDisponibles[0];
				_selectedOrigin = new Vector2I(first.Pos[0], first.Pos[1]);
				_playerRadar.SetSelectedCell(_selectedOrigin);
			}

			RequestPreview();
		}

		private void OnPlayerCellClicked(int gx, int gy)
		{
			if (_isTurnInProgress) return;
			_selectedOrigin = new Vector2I(gx, gy);
			_playerRadar.SetSelectedCell(_selectedOrigin);
			RequestPreview();
		}

		private void OnShipSelected(long index)
		{
			if (_isTurnInProgress || _sessionData == null || index < 0 || index >= _sessionData.EmisoresDisponibles.Count) return;
			var em = _sessionData.EmisoresDisponibles[(int)index];
			_selectedOrigin = new Vector2I(em.Pos[0], em.Pos[1]);
			_playerRadar.SetSelectedCell(_selectedOrigin);
			RequestPreview();
		}

		private void OnSkillSelected(long index)
		{
			_selectedSkill = index switch
			{
				0 => "suma",
				1 => "viento",
				2 => "torpedo",
				3 => "sonar",
				4 => "orbital",
				_ => "suma"
			};
			ActualizarVisibilidadSliders();
			RequestPreview();
		}

		private async void RequestPreview()
		{
			if (!_wsClient.IsConnected || _isTurnInProgress) return;

			if (_selectedSkill == "sonar")
			{
				_aimOverlay.ClearPreview();
				return;
			}

			int vx = (int)_sliderVx.Value;
			int vy = (int)_sliderVy.Value;
			int ux = (int)_sliderUx.Value;
			int uy = (int)_sliderUy.Value;
			int k = (int)_sliderK.Value;

			await _wsClient.RequestPreviewAsync(
				_selectedSkill,
				new[] { _selectedOrigin.X, _selectedOrigin.Y },
				new[] { vx, vy },
				new[] { ux, uy },
				k
			);
		}

		private void OnPreviewReceived(string json)
		{
			var preview = JsonSerializer.Deserialize<PreviewResultPayload>(json);
			if (preview == null || preview.Origen.Count < 2 || preview.Impacto.Count < 2) return;

			Vector2I orig = new(preview.Origen[0], preview.Origen[1]);
			Vector2I imp = new(preview.Impacto[0], preview.Impacto[1]);
			_predictedImpact = imp;

			_aimOverlay.SetPreview(orig, imp, preview.DentroDelMapa);
		}

		private async void OnFirePressed()
		{
			if (!_wsClient.IsConnected || _isTurnInProgress) return;

			_isTurnInProgress = true;
			_btnFire.Disabled = true;
			_btnFire.Text = "[ PROCESANDO COMBATE... ]";

			int vx = (int)_sliderVx.Value;
			int vy = (int)_sliderVy.Value;
			int ux = (int)_sliderUx.Value;
			int uy = (int)_sliderUy.Value;
			int k = (int)_sliderK.Value;

			await _wsClient.FireSkillAsync(
				_selectedSkill,
				new[] { _selectedOrigin.X, _selectedOrigin.Y },
				new[] { vx, vy },
				new[] { ux, uy },
				k
			);
		}

		private async void OnTurnResolved(string json)
		{
			var turn = JsonSerializer.Deserialize<TurnResolvedPayload>(json);
			if (turn == null)
			{
				_isTurnInProgress = false;
				_btnFire.Disabled = false;
				_btnFire.Text = "[ EJECUTAR DISPARO VECTORIAL ]";
				return;
			}

			// 1. Animación del ataque del jugador según la habilidad
			if (_selectedSkill == "sonar")
			{
				float dist = ExtraerDistanciaSonar(turn.AtaqueJugador?.Resultado);
				await _enemyRadar.AnimateSonarPulseAsync(_selectedOrigin, dist);
			}
			else if (_selectedSkill == "orbital")
			{
				await _enemyRadar.AnimateOrbitalBeamAsync(_selectedOrigin, _predictedImpact);
			}
			else
			{
				bool playerHit = DeterminarSiHuboImpacto(turn.AtaqueJugador?.Resultado);
				await _enemyRadar.AnimateShotAsync(_selectedOrigin, _predictedImpact, playerHit);
			}

			if (turn.AtaqueJugador?.Resultado != null)
			{
				ProcesarLogPedagogico(GameSettings.PlayerName.ToUpper(), turn.AtaqueJugador.Resultado);
			}

			// 2. Turno y ataque de la IA con suspenso
			if (turn.AtaqueIa != null)
			{
				_mathConsole.AppendWarning("Almirante Vector calculando vector de tiro enemigo...");
				await ToSignal(GetTree().CreateTimer(0.8f / GameSettings.AnimationSpeed), SceneTreeTimer.SignalName.Timeout);

				var aiOrigin = ExtraerOrigenIa(turn.AtaqueIa);
				var aiTarget = ExtraerObjetivoIa(turn.AtaqueIa);
				bool aiHit = DeterminarSiHuboImpacto(turn.AtaqueIa);

				await _playerRadar.AnimateShotAsync(aiOrigin, aiTarget, aiHit);
				ProcesarLogPedagogico("ALMIRANTE VECTOR (IA)", turn.AtaqueIa);
			}

			// 3. Actualizar estado
			if (turn.NuevoEstado != null)
			{
				_sessionData = turn.NuevoEstado;
				UpdateGameStateUI();

				if (_sessionData.Estado == "VICTORIA")
				{
					_mathConsole.AppendSuccess("VICTORIA TOTAL: Has aniquilado la flota del Almirante Vector.");
				}
				else if (_sessionData.Estado == "DERROTA")
				{
					_mathConsole.AppendError("DERROTA: Tu flota ha sido destruida en combate.");
				}
			}

			_isTurnInProgress = false;
			_btnFire.Disabled = false;
			_btnFire.Text = "[ EJECUTAR DISPARO VECTORIAL ]";
		}

		private float ExtraerDistanciaSonar(Dictionary<string, object>? dict)
		{
			if (dict == null) return 3.0f;
			if (dict.TryGetValue("distancia", out var d) && d is JsonElement elem)
			{
				if (elem.ValueKind == JsonValueKind.Number) return elem.GetSingle();
			}
			return 3.0f;
		}

		private bool DeterminarSiHuboImpacto(Dictionary<string, object>? dict)
		{
			if (dict == null) return false;
			if (dict.TryGetValue("resultado", out var res) && res is JsonElement elem)
			{
				if (elem.ValueKind == JsonValueKind.Object && elem.TryGetProperty("impacto", out var imp))
				{
					return imp.GetBoolean();
				}
			}
			if (dict.TryGetValue("resultado_tablero", out var resTab) && resTab is JsonElement arrElem && arrElem.ValueKind == JsonValueKind.Array)
			{
				foreach (var item in arrElem.EnumerateArray())
				{
					if (item.TryGetProperty("impacto", out var impVal) && impVal.GetBoolean())
					{
						return true;
					}
				}
			}
			return false;
		}

		private Vector2I ExtraerOrigenIa(Dictionary<string, object> dict)
		{
			try
			{
				if (dict.TryGetValue("origen", out var orig) && orig is JsonElement elem && elem.ValueKind == JsonValueKind.Array)
				{
					var arr = elem.EnumerateArray();
					int x = arr.MoveNext() ? arr.Current.GetInt32() : 5;
					int y = arr.MoveNext() ? arr.Current.GetInt32() : 5;
					return new Vector2I(x, y);
				}
			}
			catch { }
			return new Vector2I(5, 5);
		}

		private Vector2I ExtraerObjetivoIa(Dictionary<string, object> dict)
		{
			try
			{
				if (dict.TryGetValue("destino", out var dest) && dest is JsonElement dElem && dElem.ValueKind == JsonValueKind.Array)
				{
					var arr = dElem.EnumerateArray();
					int x = arr.MoveNext() ? arr.Current.GetInt32() : 0;
					int y = arr.MoveNext() ? arr.Current.GetInt32() : 0;
					return new Vector2I(x, y);
				}
				if (dict.TryGetValue("disparo", out var disp) && disp is JsonElement elem && elem.ValueKind == JsonValueKind.Array)
				{
					var arr = elem.EnumerateArray();
					int x = arr.MoveNext() ? arr.Current.GetInt32() : 0;
					int y = arr.MoveNext() ? arr.Current.GetInt32() : 0;
					return new Vector2I(x, y);
				}
			}
			catch { }
			return new Vector2I(0, 0);
		}

		private void ProcesarLogPedagogico(string autor, Dictionary<string, object> resDict)
		{
			try
			{
				if (resDict.TryGetValue("explicacion", out var expObj) && expObj is JsonElement expElem)
				{
					string operacion = expElem.TryGetProperty("operacion", out var op) ? op.GetString() ?? "" : "";
					string formula = expElem.TryGetProperty("formula", out var form) ? form.GetString() ?? "" : "";
					List<string> pasos = new();

					if (expElem.TryGetProperty("pasos", out var pasosArr) && pasosArr.ValueKind == JsonValueKind.Array)
					{
						foreach (var p in pasosArr.EnumerateArray())
						{
							pasos.Add(p.GetString() ?? "");
						}
					}

					_mathConsole.AppendMathBreakdown(autor, operacion, formula, pasos);
				}
			}
			catch (Exception ex)
			{
				GD.PrintErr($"Error parseando explicación: {ex.Message}");
			}
		}

		private void OnErrorReceived(string error)
		{
			_isTurnInProgress = false;
			_btnFire.Disabled = false;
			_btnFire.Text = "[ EJECUTAR DISPARO VECTORIAL ]";
			_mathConsole.AppendError(error);
		}
	}
}
