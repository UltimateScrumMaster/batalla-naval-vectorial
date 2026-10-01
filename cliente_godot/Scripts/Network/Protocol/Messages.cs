using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace BatallaNavalVectorial.Network.Protocol
{
    public class WsMessage<T>
    {
        [JsonPropertyName("type")]
        public string Type { get; set; } = string.Empty;

        [JsonPropertyName("payload")]
        public T? Payload { get; set; }
    }

    public class ShipCellDto
    {
        [JsonPropertyName("x")]
        public int X { get; set; }

        [JsonPropertyName("y")]
        public int Y { get; set; }

        [JsonPropertyName("impactada")]
        public bool Impactada { get; set; }
    }

    public class ShipDto
    {
        [JsonPropertyName("nombre")]
        public string Nombre { get; set; } = string.Empty;

        [JsonPropertyName("tamano")]
        public int Tamano { get; set; }

        [JsonPropertyName("icono")]
        public string Icono { get; set; } = "◆";

        [JsonPropertyName("hundido")]
        public bool Hundido { get; set; }

        [JsonPropertyName("celdas")]
        public List<ShipCellDto> Celdas { get; set; } = new();

        [JsonPropertyName("origen")]
        public List<int>? Origen { get; set; }

        [JsonPropertyName("direccion")]
        public List<int>? Direccion { get; set; }
    }

    public class BoardDto
    {
        [JsonPropertyName("ancho")]
        public int Ancho { get; set; } = 10;

        [JsonPropertyName("alto")]
        public int Alto { get; set; } = 10;

        [JsonPropertyName("es_oculto")]
        public bool EsOculto { get; set; }

        [JsonPropertyName("titulo")]
        public string Titulo { get; set; } = string.Empty;

        [JsonPropertyName("barcos")]
        public List<ShipDto> Barcos { get; set; } = new();

        [JsonPropertyName("disparos_agua")]
        public List<List<int>> DisparosAgua { get; set; } = new();

        [JsonPropertyName("disparos_acierto")]
        public List<List<int>> DisparosAcierto { get; set; } = new();

        [JsonPropertyName("rastro_proyeccion")]
        public List<List<int>> RastroProyeccion { get; set; } = new();
    }

    public class EmitterShipDto
    {
        [JsonPropertyName("barco")]
        public string Barco { get; set; } = string.Empty;

        [JsonPropertyName("pos")]
        public List<int> Pos { get; set; } = new();
    }

    public class SkillInfoDto
    {
        [JsonPropertyName("nombre")]
        public string Nombre { get; set; } = string.Empty;

        [JsonPropertyName("costo")]
        public int Costo { get; set; }
    }

    public class SessionReadyPayload
    {
        [JsonPropertyName("turno")]
        public int Turno { get; set; }

        [JsonPropertyName("energia")]
        public int Energia { get; set; }

        [JsonPropertyName("energia_max")]
        public int EnergiaMax { get; set; } = 6;

        [JsonPropertyName("viento")]
        public List<int> Viento { get; set; } = new() { 0, 0 };

        [JsonPropertyName("estado")]
        public string Estado { get; set; } = "TURNO_JUGADOR";

        [JsonPropertyName("emisores_disponibles")]
        public List<EmitterShipDto> EmisoresDisponibles { get; set; } = new();

        [JsonPropertyName("habilidades")]
        public Dictionary<string, SkillInfoDto> Habilidades { get; set; } = new();

        [JsonPropertyName("tablero_jugador")]
        public BoardDto TableroJugador { get; set; } = new();

        [JsonPropertyName("tablero_enemigo")]
        public BoardDto TableroEnemigo { get; set; } = new();
    }

    public class PreviewResultPayload
    {
        [JsonPropertyName("skill")]
        public string Skill { get; set; } = string.Empty;

        [JsonPropertyName("origen")]
        public List<int> Origen { get; set; } = new();

        [JsonPropertyName("impacto")]
        public List<int> Impacto { get; set; } = new();

        [JsonPropertyName("dentro_del_mapa")]
        public bool DentroDelMapa { get; set; }

        [JsonPropertyName("vector_recortado")]
        public List<int> VectorRecortado { get; set; } = new();
    }

    public class MathExplanationDto
    {
        [JsonPropertyName("operacion")]
        public string Operacion { get; set; } = string.Empty;

        [JsonPropertyName("formula")]
        public string Formula { get; set; } = string.Empty;

        [JsonPropertyName("pasos")]
        public List<string> Pasos { get; set; } = new();
    }

    public class AttackResultDto
    {
        [JsonPropertyName("habilidad")]
        public string Habilidad { get; set; } = string.Empty;

        [JsonPropertyName("resultado")]
        public Dictionary<string, object>? Resultado { get; set; }
    }

    public class TurnResolvedPayload
    {
        [JsonPropertyName("ataque_jugador")]
        public AttackResultDto? AtaqueJugador { get; set; }

        [JsonPropertyName("ataque_ia")]
        public Dictionary<string, object>? AtaqueIa { get; set; }

        [JsonPropertyName("nuevo_estado")]
        public SessionReadyPayload? NuevoEstado { get; set; }
    }
}
