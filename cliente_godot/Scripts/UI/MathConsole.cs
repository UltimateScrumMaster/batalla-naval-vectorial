using System.Collections.Generic;
using Godot;

namespace BatallaNavalVectorial.UI
{
	public partial class MathConsole : PanelContainer
	{
		private RichTextLabel _logLabel = null!;

		public override void _Ready()
		{
			_logLabel = new RichTextLabel
			{
				BbcodeEnabled = true,
				ScrollFollowing = true,
				CustomMinimumSize = new Vector2(300, 180),
				SelectionEnabled = true
			};
			AddChild(_logLabel);

			AppendHeader("SISTEMA DE ANÁLISIS VECTORIAL ONLINE");
			AppendInfo("Esperando cálculo de tiro...");
		}

		public void Clear()
		{
			_logLabel.Clear();
		}

		public void AppendHeader(string text)
		{
			_logLabel.AppendText($"[b][color=#00f5d4]=== {text} ===[/color][/b]\n");
		}

		public void AppendInfo(string text)
		{
			_logLabel.AppendText($"[color=#8ecae6]{text}[/color]\n");
		}

		public void AppendSuccess(string text)
		{
			_logLabel.AppendText($"[b][color=#52b788]✔ {text}[/color][/b]\n");
		}

		public void AppendWarning(string text)
		{
			_logLabel.AppendText($"[b][color=#ffb703]⚠ {text}[/color][/b]\n");
		}

		public void AppendError(string text)
		{
			_logLabel.AppendText($"[b][color=#e63946]✖ {text}[/color][/b]\n");
		}

		public void AppendMathBreakdown(string author, string skillName, string formula, List<string> steps)
		{
			string color = author == "JUGADOR" ? "#00f5d4" : "#ffb703";
			_logLabel.AppendText($"\n[b][color={color}]▶ [{author}] {skillName.ToUpper()}[/color][/b]\n");
			_logLabel.AppendText($"[i][color=#caf0f8]Fórmula: {formula}[/color][/i]\n");

			foreach (var step in steps)
			{
				_logLabel.AppendText($"  [color=#e0e1dd]{step}[/color]\n");
			}
		}
	}
}
