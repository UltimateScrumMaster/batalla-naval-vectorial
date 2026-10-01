using System;
using System.IO;
using System.Net.WebSockets;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using BatallaNavalVectorial.Network.Protocol;
using Godot;

namespace BatallaNavalVectorial.Network
{
    public partial class WebSocketClient : Node
    {
        [Signal]
        public delegate void ConnectedEventHandler();

        [Signal]
        public delegate void DisconnectedEventHandler();

        [Signal]
        public delegate void SessionReadyEventHandler(string sessionJson);

        [Signal]
        public delegate void PreviewReceivedEventHandler(string previewJson);

        [Signal]
        public delegate void TurnResolvedEventHandler(string turnJson);

        [Signal]
        public delegate void ErrorReceivedEventHandler(string errorMessage);

        private ClientWebSocket? _client;
        private CancellationTokenSource? _cts;
        private bool _isConnected = false;

        public bool IsConnected => _isConnected;

        public async Task ConnectToServerAsync(string uri = "ws://127.0.0.1:8765")
        {
            try
            {
                _client = new ClientWebSocket();
                _cts = new CancellationTokenSource();

                GD.Print($"[WebSocketClient] Conectando a {uri}...");
                await _client.ConnectAsync(new Uri(uri), _cts.Token);
                _isConnected = true;
                EmitSignal(SignalName.Connected);

                _ = Task.Run(ReceiveLoopAsync, _cts.Token);
            }
            catch (Exception ex)
            {
                GD.PrintErr($"[WebSocketClient] Error al conectar: {ex.Message}");
                _isConnected = false;
                EmitSignal(SignalName.ErrorReceived, $"No se pudo conectar al servidor WebSocket ({ex.Message})");
            }
        }

        public async Task StartGameAsync(int? seed = null)
        {
            var msg = new
            {
                type = "START_GAME",
                payload = seed.HasValue ? new { semilla = seed.Value } : new object()
            };
            await SendJsonAsync(msg);
        }

        public async Task RequestPreviewAsync(string skill, int[] origin, int[] vectorV, int[]? vectorU = null, int k = 1)
        {
            var msg = new
            {
                type = "GET_PREVIEW",
                payload = new
                {
                    habilidad = skill,
                    origen = origin,
                    vector_v = vectorV,
                    vector_u = vectorU ?? new[] { 1, 0 },
                    k = k
                }
            };
            await SendJsonAsync(msg);
        }

        public async Task FireSkillAsync(string skill, int[] origin, int[] vectorV, int[]? vectorU = null, int k = 1)
        {
            var msg = new
            {
                type = "FIRE_SKILL",
                payload = new
                {
                    habilidad = skill,
                    origen = origin,
                    vector_v = vectorV,
                    vector_u = vectorU ?? new[] { 1, 0 },
                    k = k
                }
            };
            await SendJsonAsync(msg);
        }

        private async Task SendJsonAsync<T>(T messageObject)
        {
            if (_client == null || _client.State != WebSocketState.Open)
            {
                GD.PrintErr("[WebSocketClient] No se puede enviar mensaje: socket cerrado.");
                return;
            }

            string json = JsonSerializer.Serialize(messageObject);
            byte[] bytes = Encoding.UTF8.GetBytes(json);
            await _client.SendAsync(new ArraySegment<byte>(bytes), WebSocketMessageType.Text, true, CancellationToken.None);
        }

        private async Task ReceiveLoopAsync()
        {
            var buffer = new byte[8192];
            while (_client != null && _client.State == WebSocketState.Open && !_cts!.Token.IsCancellationRequested)
            {
                try
                {
                    using var ms = new MemoryStream();
                    WebSocketReceiveResult result;
                    do
                    {
                        result = await _client.ReceiveAsync(new ArraySegment<byte>(buffer), _cts.Token);
                        if (result.MessageType == WebSocketMessageType.Close)
                        {
                            await _client.CloseAsync(WebSocketCloseStatus.NormalClosure, "Closing", CancellationToken.None);
                            _isConnected = false;
                            Callable.From(() => EmitSignal(SignalName.Disconnected)).CallDeferred();
                            return;
                        }
                        ms.Write(buffer, 0, result.Count);
                    }
                    while (!result.EndOfMessage);

                    string jsonText = Encoding.UTF8.GetString(ms.ToArray());
                    DispatchMessage(jsonText);
                }
                catch (Exception ex)
                {
                    if (!_cts!.Token.IsCancellationRequested)
                    {
                        GD.PrintErr($"[WebSocketClient] Error en ReceiveLoop: {ex.Message}");
                    }
                    _isConnected = false;
                    Callable.From(() => EmitSignal(SignalName.Disconnected)).CallDeferred();
                    break;
                }
            }
        }

        private void DispatchMessage(string jsonText)
        {
            try
            {
                using var doc = JsonDocument.Parse(jsonText);
                string msgType = doc.RootElement.GetProperty("type").GetString() ?? "";
                string payloadJson = doc.RootElement.GetProperty("payload").GetRawText();

                Callable.From(() =>
                {
                    switch (msgType)
                    {
                        case "SESSION_READY":
                        case "STATE_UPDATE":
                            EmitSignal(SignalName.SessionReady, payloadJson);
                            break;
                        case "PREVIEW_RESULT":
                            EmitSignal(SignalName.PreviewReceived, payloadJson);
                            break;
                        case "TURN_RESOLVED":
                            EmitSignal(SignalName.TurnResolved, payloadJson);
                            break;
                        case "ERROR":
                            EmitSignal(SignalName.ErrorReceived, payloadJson);
                            break;
                        default:
                            GD.Print($"[WebSocketClient] Mensaje no manejado: {msgType}");
                            break;
                    }
                }).CallDeferred();
            }
            catch (Exception ex)
            {
                GD.PrintErr($"[WebSocketClient] Error deserializando JSON: {ex.Message}");
            }
        }

        public override void _ExitTree()
        {
            _cts?.Cancel();
            _client?.Dispose();
            base._ExitTree();
        }
    }
}
