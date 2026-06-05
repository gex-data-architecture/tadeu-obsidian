---
tipo: function
definer: "gabriel_gomes@%"
determinismo: "YES"
acesso_sql: "NO SQL"
security: "DEFINER"
criada_em: "2025-10-30 17:34:44"
alterada_em: "2025-10-30 17:34:44"
execucoes: ""
tags: [rotina, function]
---

# calcular_horas_uteis

## Dependências

- **Lê:** —
- **Escreve:** —
- **Cria:** —
- **Trunca:** —
- **Dropa:** —
- **Chama:** —

## Chamada por
—

## Execuções (performance_schema)

> Sem execuções na janela atual (zera a cada restart do MySQL). Pode nunca ter rodado desde o último restart, ou sem acesso ao `performance_schema`.

## Corpo SQL

```sql
BEGIN
    DECLARE horas_totais DECIMAL(10,2);
    DECLARE horas_fds DECIMAL(10,2);
    DECLARE dias_diferenca INT;
    DECLARE dia_atual DATE;
    DECLARE dia_semana_atual INT;
    DECLARE hora_inicio_decimal DECIMAL(10,2);
    DECLARE hora_fim_decimal DECIMAL(10,2);
    DECLARE contador INT;

    -- Se alguma data for NULL, retorna NULL
    IF data_inicio IS NULL OR data_fim IS NULL THEN
        RETURN NULL;
    END IF;

    -- Se data_fim for antes de data_inicio, retorna 0
    IF data_fim < data_inicio THEN
        RETURN 0;
    END IF;

    -- Calcula dias e horas
    SET dias_diferenca = DATEDIFF(data_fim, data_inicio);
    SET hora_inicio_decimal = HOUR(data_inicio) + MINUTE(data_inicio) / 60.0;
    SET hora_fim_decimal = HOUR(data_fim) + MINUTE(data_fim) / 60.0;

    -- CASO 1: MESMO DIA
    IF dias_diferenca = 0 THEN
        SET dia_semana_atual = DAYOFWEEK(data_inicio);
        -- Se for sábado ou domingo, retorna 0
        IF dia_semana_atual = 1 OR dia_semana_atual = 7 THEN
            RETURN 0;
        ELSE
            -- É dia útil, retorna diferença de horas
            RETURN hora_fim_decimal - hora_inicio_decimal;
        END IF;
    END IF;

    -- CASO 2: DIAS DIFERENTES
    -- Calcula horas totais
    SET horas_totais = TIMESTAMPDIFF(MINUTE, data_inicio, data_fim) / 60.0;
    SET horas_fds = 0;

    -- Loop por cada dia no intervalo
    SET contador = 0;
    WHILE contador <= dias_diferenca DO
            SET dia_atual = DATE_ADD(DATE(data_inicio), INTERVAL contador DAY);
            SET dia_semana_atual = DAYOFWEEK(dia_atual);

            -- Se é fim de semana (sábado=7 ou domingo=1)
            IF dia_semana_atual = 1 OR dia_semana_atual = 7 THEN

                -- PRIMEIRO DIA (pode ser parcial)
                IF contador = 0 THEN
                    -- Subtrai do início do dia até meia-noite
                    SET horas_fds = horas_fds + (24.0 - hora_inicio_decimal);

                    -- ÚLTIMO DIA (pode ser parcial)
                ELSEIF contador = dias_diferenca THEN
                    -- Subtrai da meia-noite até a hora final
                    SET horas_fds = horas_fds + hora_fim_decimal;

                    -- DIAS INTERMEDIÁRIOS (fim de semana completo)
                ELSE
                    SET horas_fds = horas_fds + 24.0;
                END IF;

            END IF;

            SET contador = contador + 1;
        END WHILE;

    -- Retorna horas totais menos horas de fim de semana
    RETURN GREATEST(0.0, horas_totais - horas_fds);
END
```
