using System;
using Godot;

namespace BatallaNavalVectorial.UI
{
	public partial class VectorAimOverlay : Control
	{
		private Vector2I _origin = Vector2I.Zero;
		private Vector2I _impact = Vector2I.Zero;
		private bool _isInsideMap = true;
		private bool _isVisible = false;

		private const float CellPixelSize = 34.0f;
		private const float MarginLeft = 28.0f;

		private readonly Color _colorValid = new(0.2f, 0.95f, 0.4f, 0.9f);
		private readonly Color _colorInvalid = new(0.95f, 0.2f, 0.2f, 0.9f);
		private readonly Color _colorOriginPoint = new(1.0f, 0.85f, 0.1f, 1.0f);

		public void SetPreview(Vector2I origin, Vector2I impact, bool isInsideMap)
		{
			_origin = origin;
			_impact = impact;
			_isInsideMap = isInsideMap;
			_isVisible = true;
			QueueRedraw();
		}

		public void ClearPreview()
		{
			_isVisible = false;
			QueueRedraw();
		}

		public override void _Draw()
		{
			if (!_isVisible) return;

			Vector2 screenOrigin = GridToScreen(_origin);
			Vector2 screenImpact = GridToScreen(_impact);
			Color arrowColor = _isInsideMap ? _colorValid : _colorInvalid;

			// 1. Punto de origen
			DrawCircle(screenOrigin, 5.0f, _colorOriginPoint);

			// 2. Si hay desplazamiento, dibujar flecha
			if (screenOrigin.DistanceTo(screenImpact) > 2.0f)
			{
				DrawLine(screenOrigin, screenImpact, arrowColor, 3.0f, true);

				// Punta de la flecha
				Vector2 dir = (screenImpact - screenOrigin).Normalized();
				Vector2 perp = new(-dir.Y, dir.X);
				float arrowSize = 12.0f;

				Vector2 p1 = screenImpact;
				Vector2 p2 = screenImpact - dir * arrowSize + perp * (arrowSize * 0.5f);
				Vector2 p3 = screenImpact - dir * arrowSize - perp * (arrowSize * 0.5f);

				DrawColoredPolygon(new[] { p1, p2, p3 }, arrowColor);
			}

			// 3. Retícula / Mira de impacto
			DrawCircle(screenImpact, 8.0f, new Color(arrowColor.R, arrowColor.G, arrowColor.B, 0.3f));
			DrawArc(screenImpact, 10.0f, 0, Mathf.Tau, 24, arrowColor, 2.0f);
		}

		private Vector2 GridToScreen(Vector2I gridPos)
		{
			float px = MarginLeft + gridPos.X * CellPixelSize + CellPixelSize * 0.5f;
			float py = 20.0f + (9 - gridPos.Y) * CellPixelSize + CellPixelSize * 0.5f;
			return new Vector2(px, py);
		}
	}
}
