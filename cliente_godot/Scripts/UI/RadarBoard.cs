using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using BatallaNavalVectorial.Network.Protocol;
using Godot;

namespace BatallaNavalVectorial.UI
{
	public partial class RadarBoard : Control
	{
		[Signal]
		public delegate void CellClickedEventHandler(int x, int y);

		[Export]
		public bool IsEnemyRadar { get; set; } = false;

		[Export]
		public string Title { get; set; } = "TABLERO";

		private const int GridSize = 10;
		private const float CellPixelSize = 34.0f;
		private const float MarginLeft = 28.0f;
		private const float MarginBottom = 28.0f;

		private BoardDto? _boardData;
		private Vector2I? _selectedCell;

		// Variables para animación de proyectil
		private bool _isAnimatingShot = false;
		private Vector2 _shotStartPos;
		private Vector2 _shotCurrentPos;
		private Vector2 _shotTargetPos;

		// Variables para animación de impacto
		private bool _isAnimatingImpact = false;
		private Vector2 _impactPos;
		private float _impactRadius = 0f;
		private Color _impactColor;

		// Variables para animación de Sónar (Onda expansiva)
		private bool _isAnimatingSonar = false;
		private Vector2 _sonarOriginPos;
		private float _sonarCurrentRadius = 0f;
		private float _sonarMaxRadius = 0f;

		// Variables para animación de Rayo Orbital (Láser Satelital)
		private bool _isAnimatingOrbital = false;
		private Vector2 _orbitalStartPos;
		private Vector2 _orbitalEndPos;
		private float _orbitalBeamWidth = 0f;

		public override void _Ready()
		{
			CustomMinimumSize = new Vector2(MarginLeft + GridSize * CellPixelSize + 10, MarginBottom + GridSize * CellPixelSize + 30);
		}

		public void UpdateBoard(BoardDto board)
		{
			_boardData = board;
			QueueRedraw();
		}

		public void SetSelectedCell(Vector2I? cell)
		{
			_selectedCell = cell;
			QueueRedraw();
		}

		public async Task AnimateShotAsync(Vector2I origin, Vector2I target, bool isHit)
		{
			if (!GameSettings.EnableAnimations)
			{
				QueueRedraw();
				return;
			}

			_shotStartPos = GridToScreenCenter(origin);
			_shotTargetPos = GridToScreenCenter(target);
			_shotCurrentPos = _shotStartPos;
			_isAnimatingShot = true;

			float duration = 0.5f / GameSettings.AnimationSpeed;
			var tween = CreateTween();
			tween.TweenMethod(Callable.From<float>(t =>
			{
				_shotCurrentPos = _shotStartPos.Lerp(_shotTargetPos, t);
				QueueRedraw();
			}), 0.0f, 1.0f, duration).SetTrans(Tween.TransitionType.Quad).SetEase(Tween.EaseType.Out);

			await ToSignal(tween, Tween.SignalName.Finished);
			_isAnimatingShot = false;

			await AnimateImpactAsync(target, isHit);
		}

		public async Task AnimateImpactAsync(Vector2I target, bool isHit)
		{
			if (!GameSettings.EnableAnimations)
			{
				QueueRedraw();
				return;
			}

			_impactPos = GridToScreenCenter(target);
			_impactColor = isHit ? new Color(1.0f, 0.2f, 0.1f, 0.95f) : new Color(0.2f, 0.7f, 1.0f, 0.8f);
			_isAnimatingImpact = true;
			_impactRadius = 4.0f;

			float duration = 0.4f / GameSettings.AnimationSpeed;
			var tween = CreateTween();
			tween.TweenMethod(Callable.From<float>(r =>
			{
				_impactRadius = r;
				QueueRedraw();
			}), 4.0f, 22.0f, duration).SetTrans(Tween.TransitionType.Circ).SetEase(Tween.EaseType.Out);

			await ToSignal(tween, Tween.SignalName.Finished);
			_isAnimatingImpact = false;
			QueueRedraw();
		}

		public async Task AnimateSonarPulseAsync(Vector2I origin, float distance)
		{
			if (!GameSettings.EnableAnimations)
			{
				QueueRedraw();
				return;
			}

			_sonarOriginPos = GridToScreenCenter(origin);
			_sonarMaxRadius = Math.Max(distance * CellPixelSize, CellPixelSize * 2.5f);
			_sonarCurrentRadius = 2.0f;
			_isAnimatingSonar = true;

			float duration = 0.8f / GameSettings.AnimationSpeed;
			var tween = CreateTween();
			tween.TweenMethod(Callable.From<float>(r =>
			{
				_sonarCurrentRadius = r;
				QueueRedraw();
			}), 2.0f, _sonarMaxRadius, duration).SetTrans(Tween.TransitionType.Quad).SetEase(Tween.EaseType.Out);

			await ToSignal(tween, Tween.SignalName.Finished);
			_isAnimatingSonar = false;
			QueueRedraw();
		}

		public async Task AnimateOrbitalBeamAsync(Vector2I origin, Vector2I endPoint)
		{
			if (!GameSettings.EnableAnimations)
			{
				QueueRedraw();
				return;
			}

			_orbitalStartPos = GridToScreenCenter(origin);
			_orbitalEndPos = GridToScreenCenter(endPoint);
			_isAnimatingOrbital = true;
			_orbitalBeamWidth = 14.0f;

			float duration = 0.6f / GameSettings.AnimationSpeed;
			var tween = CreateTween();
			tween.TweenMethod(Callable.From<float>(w =>
			{
				_orbitalBeamWidth = w;
				QueueRedraw();
			}), 16.0f, 1.0f, duration).SetTrans(Tween.TransitionType.Expo).SetEase(Tween.EaseType.In);

			await ToSignal(tween, Tween.SignalName.Finished);
			_isAnimatingOrbital = false;
			QueueRedraw();
		}

		public override void _GuiInput(InputEvent @event)
		{
			if (@event is InputEventMouseButton mb && mb.Pressed && mb.ButtonIndex == MouseButton.Left)
			{
				var localPos = mb.Position;
				int gx = Mathf.FloorToInt((localPos.X - MarginLeft) / CellPixelSize);
				int gy = 9 - Mathf.FloorToInt((localPos.Y - 20.0f) / CellPixelSize);

				if (gx >= 0 && gx < GridSize && gy >= 0 && gy < GridSize)
				{
					EmitSignal(SignalName.CellClicked, gx, gy);
				}
			}
		}

		public override void _Draw()
		{
			Color colorBg = GameSettings.GetThemeColorBackground();
			Color colorGrid = GameSettings.GetThemeColorGrid();
			Color colorAxis = GameSettings.GetThemeColorPrimary();
			Color colorAccent = GameSettings.GetThemeColorAccent();

			Color colorShipAlly = new(0.18f, 0.65f, 0.38f, 0.95f);
			Color colorShipDamaged = new(0.9f, 0.2f, 0.2f, 0.95f);
			Color colorMiss = new(0.3f, 0.6f, 0.85f, 0.7f);
			Color colorHit = new(1.0f, 0.25f, 0.25f, 1.0f);
			Color colorSelection = new(1.0f, 0.84f, 0.0f, 1.0f);
			Color colorProjection = new(1.0f, 0.55f, 0.0f, 0.6f);

			// 1. Fondo del Radar
			DrawRect(new Rect2(Vector2.Zero, Size), colorBg, true);
			DrawRect(new Rect2(Vector2.Zero, Size), colorGrid, false, 2.0f);

			// Título
			DrawString(ThemeDB.FallbackFont, new Vector2(MarginLeft, 16), Title, HorizontalAlignment.Left, -1, 13, colorAxis);

			// 2. Grilla y Ejes (0..9)
			for (int i = 0; i <= GridSize; i++)
			{
				float x = MarginLeft + i * CellPixelSize;
				float yTop = 20.0f;
				float yBottom = 20.0f + GridSize * CellPixelSize;
				DrawLine(new Vector2(x, yTop), new Vector2(x, yBottom), colorGrid, 1.0f);

				float y = 20.0f + i * CellPixelSize;
				float xLeft = MarginLeft;
				float xRight = MarginLeft + GridSize * CellPixelSize;
				DrawLine(new Vector2(xLeft, y), new Vector2(xRight, y), colorGrid, 1.0f);
			}

			// Etiquetas numéricas de ejes
			for (int i = 0; i < GridSize; i++)
			{
				float x = MarginLeft + i * CellPixelSize + CellPixelSize * 0.35f;
				float y = 20.0f + GridSize * CellPixelSize + 16.0f;
				DrawString(ThemeDB.FallbackFont, new Vector2(x, y), i.ToString(), HorizontalAlignment.Left, -1, 11, colorAxis);

				float labelY = 20.0f + (9 - i) * CellPixelSize + CellPixelSize * 0.65f;
				DrawString(ThemeDB.FallbackFont, new Vector2(MarginLeft - 18, labelY), i.ToString(), HorizontalAlignment.Left, -1, 11, colorAxis);
			}

			if (_boardData != null)
			{
				// 3. Barcos
				foreach (var barco in _boardData.Barcos)
				{
					foreach (var celda in barco.Celdas)
					{
						var rect = ObtenerRectCelda(celda.X, celda.Y);
						Color colorCelda = celda.Impactada ? colorShipDamaged : colorShipAlly;
						DrawRect(rect.Grow(-2), colorCelda, true);
						DrawRect(rect.Grow(-2), colorAccent, false, 1.0f);
					}
				}

				// 4. Rastros de Proyección
				foreach (var pos in _boardData.RastroProyeccion)
				{
					if (pos.Count >= 2)
					{
						var rect = ObtenerRectCelda(pos[0], pos[1]);
						DrawRect(rect.Grow(-4), colorProjection, true);
					}
				}

				// 5. Disparos al Agua
				foreach (var pos in _boardData.DisparosAgua)
				{
					if (pos.Count >= 2)
					{
						var rect = ObtenerRectCelda(pos[0], pos[1]);
						var center = rect.GetCenter();
						DrawLine(center + new Vector2(-6, -6), center + new Vector2(6, 6), colorMiss, 2.0f);
						DrawLine(center + new Vector2(6, -6), center + new Vector2(-6, 6), colorMiss, 2.0f);
					}
				}

				// 6. Impactos Certeros
				foreach (var pos in _boardData.DisparosAcierto)
				{
					if (pos.Count >= 2)
					{
						var rect = ObtenerRectCelda(pos[0], pos[1]);
						var center = rect.GetCenter();
						DrawCircle(center, 7.0f, colorHit);
						DrawLine(center + new Vector2(-8, -8), center + new Vector2(8, 8), Colors.White, 2.0f);
						DrawLine(center + new Vector2(8, -8), center + new Vector2(-8, 8), Colors.White, 2.0f);
					}
				}

				// 7. Borde de Selección de Emisor
				if (_selectedCell.HasValue)
				{
					var selRect = ObtenerRectCelda(_selectedCell.Value.X, _selectedCell.Value.Y);
					DrawRect(selRect.Grow(-1), colorSelection, false, 3.0f);
				}
			}

			// 8. Animación de Proyectil en Vuelo
			if (_isAnimatingShot)
			{
				DrawLine(_shotStartPos, _shotCurrentPos, new Color(colorAxis.R, colorAxis.G, colorAxis.B, 0.4f), 2.0f);
				DrawCircle(_shotCurrentPos, 5.0f, Colors.White);
				DrawCircle(_shotCurrentPos, 3.0f, colorAxis);
			}

			// 9. Animación de Impacto (Onda expansiva / Explosión)
			if (_isAnimatingImpact)
			{
				DrawCircle(_impactPos, _impactRadius, new Color(_impactColor.R, _impactColor.G, _impactColor.B, 0.35f));
				DrawArc(_impactPos, _impactRadius, 0, Mathf.Tau, 24, _impactColor, 2.5f);
			}

			// 10. Animación de Sónar (Onda acústica concéntrica)
			if (_isAnimatingSonar)
			{
				DrawArc(_sonarOriginPos, _sonarCurrentRadius, 0, Mathf.Tau, 36, new Color(0.2f, 0.95f, 0.9f, 0.85f), 3.0f);
				DrawArc(_sonarOriginPos, Math.Max(0, _sonarCurrentRadius - 15f), 0, Mathf.Tau, 36, new Color(0.2f, 0.95f, 0.9f, 0.4f), 1.5f);
			}

			// 11. Animación de Cañón Orbital (Láser Satelital)
			if (_isAnimatingOrbital)
			{
				// Resplandor exterior
				DrawLine(_orbitalStartPos, _orbitalEndPos, new Color(0.3f, 0.8f, 1.0f, 0.5f), _orbitalBeamWidth * 2.0f, true);
				// Núcleo brillante
				DrawLine(_orbitalStartPos, _orbitalEndPos, Colors.White, _orbitalBeamWidth, true);
				DrawCircle(_orbitalStartPos, _orbitalBeamWidth * 1.5f, Colors.White);
				DrawCircle(_orbitalEndPos, _orbitalBeamWidth * 1.5f, Colors.White);
			}
		}

		private Rect2 ObtenerRectCelda(int gx, int gy)
		{
			float px = MarginLeft + gx * CellPixelSize;
			float py = 20.0f + (9 - gy) * CellPixelSize;
			return new Rect2(px, py, CellPixelSize, CellPixelSize);
		}

		private Vector2 GridToScreenCenter(Vector2I gridPos)
		{
			float px = MarginLeft + gridPos.X * CellPixelSize + CellPixelSize * 0.5f;
			float py = 20.0f + (9 - gridPos.Y) * CellPixelSize + CellPixelSize * 0.5f;
			return new Vector2(px, py);
		}
	}
}
