import math
from datetime import datetime, date
from decimal import Decimal
import conexion

db = conexion.Conexion()

class crud_impuestos:
    def consultar_productos(self):
        return db.consultar("SELECT * FROM productos ORDER BY codigo ASC")

    def consultar_tarifas(self, codigo_producto=None):
        if codigo_producto:
            sql = "SELECT * FROM tarifas WHERE codigoProducto = %s ORDER BY desde ASC"
            return db.consultar(sql, (codigo_producto,))
        return db.consultar("SELECT * FROM tarifas ORDER BY codigoProducto, desde ASC")

    def calcular_impuesto(self, codigo_producto, balance):
        """
        Calcula el impuesto mensual según la Sección 10 y Criterios de Aceptación del Documento.
        """
        try:
            balance = float(balance)
        except (ValueError, TypeError):
            return {"ok": False, "msg": "Ingrese un balance mayor que cero."}

        if balance <= 0:
            return {"ok": False, "msg": "Ingrese un balance mayor que cero."}

        # Validar existencia de producto
        if not codigo_producto or codigo_producto not in ['11801', '11802']:
            return {"ok": False, "msg": "Confirme si la actividad corresponde a comercio o industria."}

        # Buscar tarifa vigente con rango inclusivo: TarifaDesde <= Balance <= TarifaHasta (RF 10)
        sql = """
            SELECT * FROM tarifas 
            WHERE codigoProducto = %s 
              AND %s >= desde 
              AND %s <= hasta 
              AND vigente = 1
        """
        tarifas = db.consultar(sql, (codigo_producto, balance, balance))

        if not tarifas or len(tarifas) == 0:
            # RF 11, CA 10, CA 15
            return {"ok": False, "msg": "No existe una tarifa configurada para el balance indicado."}

        if len(tarifas) > 1:
            # RF 12
            return {"ok": False, "msg": "Existe más de una tarifa aplicable. Corrija la tabla tarifaria."}

        tarifa = tarifas[0]
        precio_base = float(tarifa['precioBase'])
        adicional = float(tarifa['adicional'])
        porcentaje = float(tarifa['porcentaje'])
        desde = float(tarifa['desde'])
        hasta = float(tarifa['hasta'])

        # Seccion 10: Formula de Calculo
        if porcentaje > 0:
            # Seccion 10.4 y CA 13: Tarifa porcentual
            impuesto_mensual = round(balance * (porcentaje / 100.0), 2)
            excedente = 0.0
            bloques = 0
            formula = f"${balance:,.2f} x {porcentaje:.2f}% / 100 = ${impuesto_mensual:,.2f}"
        else:
            # Seccion 10.1: Tarifa por bloques
            if balance == desde:
                # CA 04: Si el balance coincide con el inicio, bloques adicionales = 0
                excedente = 0.0
                bloques = 0
                impuesto_mensual = round(precio_base, 2)
                formula = f"Precio base: ${precio_base:.2f} (sin bloque adicional)"
            else:
                excedente = round(balance - desde, 2)
                bloques = math.ceil(excedente / 1000.0)
                adicional_total = round(bloques * adicional, 2)
                impuesto_mensual = round(precio_base + adicional_total, 2)
                formula = f"${precio_base:.2f} + ({bloques} x ${adicional:.2f}) = ${impuesto_mensual:,.2f}"

        cantidad = 1.00
        subtotal = round(cantidad * impuesto_mensual, 2)

        return {
            "ok": True,
            "codigoProducto": codigo_producto,
            "balance": balance,
            "tarifaDesde": desde,
            "tarifaHasta": hasta,
            "rangoTexto": f"${desde:,.2f} a ${hasta:,.2f}",
            "precioBase": precio_base,
            "excedente": excedente,
            "bloques": bloques,
            "adicional": adicional,
            "porcentaje": porcentaje,
            "impuestoMensual": impuesto_mensual,
            "cantidad": cantidad,
            "subtotal": subtotal,
            "formula": formula
        }

    def sincronizar_estados(self):
        """
        Mantiene los estados al día con la fecha actual del sistema:
        - Si hasta <= hoy: Histórico (ya venció)
        - Si desde <= hoy < hasta: Vigente (período en curso)
        - Si desde > hoy: Futuro (aún no entra en vigencia)
        """
        hoy = date.today()
        db.ejecutar("UPDATE periodos_actividades_economicas SET estado = 'Histórico' WHERE hasta <= %s AND estado != 'Histórico'", (hoy,))
        db.ejecutar("UPDATE periodos_actividades_economicas SET estado = 'Vigente' WHERE desde <= %s AND hasta > %s AND estado != 'Vigente'", (hoy, hoy))
        db.ejecutar("UPDATE periodos_actividades_economicas SET estado = 'Futuro' WHERE desde > %s AND estado != 'Futuro'", (hoy,))

    def consultar_periodos(self, id_cliente, codigo_producto=None):
        self.sincronizar_estados()
        hoy = date.today()

        if codigo_producto:
            sql = """
                SELECT p.*, prod.nombre as nombreProducto 
                FROM periodos_actividades_economicas p
                LEFT JOIN productos prod ON p.codigoProducto = prod.codigo
                WHERE p.idCliente = %s AND p.codigoProducto = %s
                ORDER BY p.desde ASC
            """
            periodos = db.consultar(sql, (id_cliente, codigo_producto))
        else:
            sql = """
                SELECT p.*, prod.nombre as nombreProducto 
                FROM periodos_actividades_economicas p
                LEFT JOIN productos prod ON p.codigoProducto = prod.codigo
                WHERE p.idCliente = %s
                ORDER BY p.desde ASC
            """
            periodos = db.consultar(sql, (id_cliente,))

        if periodos is None:
            periodos = []

        total_referencial = 0.0
        impuesto_vigente = 0.0

        for p in periodos:
            p['balance'] = float(p['balance'])
            p['precio'] = float(p['precio'])
            p['subtotal'] = float(p['subtotal'])
            p['cantidad'] = float(p['cantidad'])
            
            # Formatear fechas a string ISO
            if isinstance(p['desde'], (date, datetime)):
                p['desde_str'] = p['desde'].strftime('%Y-%m-%d')
                f_desde = p['desde'] if isinstance(p['desde'], date) else p['desde'].date()
            else:
                p['desde_str'] = str(p['desde'])
                f_desde = datetime.strptime(p['desde_str'], '%Y-%m-%d').date()
                
            if isinstance(p['hasta'], (date, datetime)):
                p['hasta_str'] = p['hasta'].strftime('%Y-%m-%d')
                f_hasta = p['hasta'] if isinstance(p['hasta'], date) else p['hasta'].date()
            else:
                p['hasta_str'] = str(p['hasta'])
                f_hasta = datetime.strptime(p['hasta_str'], '%Y-%m-%d').date()

            # RF 21: Total administrativo referencial (suma visual de filas históricas)
            total_referencial += p['precio']

            # Estado temporal dinámico:
            if f_hasta <= hoy:
                p['estado'] = 'Histórico'
            elif f_desde <= hoy < f_hasta:
                p['estado'] = 'Vigente'
                impuesto_vigente = p['precio']
            else:
                p['estado'] = 'Futuro'

        return {
            "periodos": periodos,
            "totalReferencial": round(total_referencial, 2),
            "impuestoVigente": round(impuesto_vigente, 2),
            "tieneVigente": (impuesto_vigente > 0)
        }

    def guardar_periodo(self, datos):
        try:
            id_cliente = datos.get('idCliente')
            codigo_producto = datos.get('codigoProducto')
            desde_str = datos.get('desde')
            hasta_str = datos.get('hasta')
            balance_raw = datos.get('balance')
            accion = datos.get('accion', 'nuevo')
            id_periodo = datos.get('idPeriodo')
            usuario = datos.get('usuario', 'admin')

            # 1. Validar Cliente tipo Empresa
            cli_res = db.consultar("SELECT tipo, nombre FROM clientes WHERE idCliente = %s", (id_cliente,))
            if not cli_res or len(cli_res) == 0:
                return {"ok": False, "msg": "Cliente no encontrado."}
            if cli_res[0]['tipo'].lower() != 'empresa':
                return {"ok": False, "msg": "El Impuesto a las Actividades Económicas requiere un cliente de tipo empresa."}

            # 2. Validar Producto
            if not codigo_producto or codigo_producto not in ['11801', '11802']:
                return {"ok": False, "msg": "Confirme si la actividad corresponde a comercio o industria."}

            # 3. Validar Balance
            try:
                balance = float(balance_raw)
            except (ValueError, TypeError):
                return {"ok": False, "msg": "Ingrese un balance mayor que cero."}

            if balance <= 0:
                return {"ok": False, "msg": "Ingrese un balance mayor que cero."}

            # 4. Validar Fechas (RF 02, RF 03)
            try:
                f_desde = datetime.strptime(desde_str, '%Y-%m-%d').date()
                f_hasta = datetime.strptime(hasta_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                return {"ok": False, "msg": "Formato de fechas inválido (use YYYY-MM-DD)."}

            if f_hasta <= f_desde:
                return {"ok": False, "msg": "La fecha Hasta debe ser posterior a la fecha Desde."}

            # 5. Validar periodos superpuestos [Desde, Hasta) (RF 04, CA 14)
            # D1 < H2 AND H1 > D2
            sql_check = """
                SELECT idPeriodo, desde, hasta, estado, esFacturado 
                FROM periodos_actividades_economicas 
                WHERE idCliente = %s 
                  AND codigoProducto = %s 
                  AND desde < %s 
                  AND hasta > %s
            """
            params_check = [id_cliente, codigo_producto, f_hasta.strftime('%Y-%m-%d'), f_desde.strftime('%Y-%m-%d')]
            if accion == 'modificar' and id_periodo:
                sql_check += " AND idPeriodo != %s"
                params_check.append(id_periodo)

            superpuestos = db.consultar(sql_check, tuple(params_check))
            if superpuestos and len(superpuestos) > 0:
                return {"ok": False, "msg": "El período indicado se superpone con un período existente."}

            # 6. Calcular impuesto y validar tarifa existente (RF 10, RF 11, RF 12, RF 13)
            calc = self.calcular_impuesto(codigo_producto, balance)
            if not calc.get('ok'):
                return calc

            # 7. Si es modificación, validar inmutabilidad de periodos facturados (RF 09, RF 14)
            if accion == 'modificar' and id_periodo:
                periodo_actual = db.consultar("SELECT * FROM periodos_actividades_economicas WHERE idPeriodo = %s", (id_periodo,))
                if periodo_actual and periodo_actual[0].get('esFacturado') == 1:
                    return {"ok": False, "msg": "El período ya fue utilizado en recibos y no puede recalcularse automáticamente."}

            # Preparar valores
            cantidad = 1.00
            precio = calc['impuestoMensual']
            subtotal = calc['subtotal']
            tarifa_rango = calc['rangoTexto']
            formula_aplicada = calc['formula']

            # Estado según fecha actual
            hoy = date.today()
            if f_hasta <= hoy:
                estado = 'Histórico'
            elif f_desde <= hoy < f_hasta:
                estado = 'Vigente'
            else:
                estado = 'Futuro'

            # Si es nuevo: si este nuevo periodo entra como Vigente, pasar cualquier anterior que estuviera vigente a Histórico
            if accion == 'nuevo':
                if estado == 'Vigente':
                    db.ejecutar("""
                        UPDATE periodos_actividades_economicas 
                        SET estado = 'Histórico' 
                        WHERE idCliente = %s AND codigoProducto = %s AND idPeriodo != LAST_INSERT_ID()
                    """, (id_cliente, codigo_producto))

                sql_ins = """
                    INSERT INTO periodos_actividades_economicas 
                    (idCliente, codigoProducto, desde, hasta, balance, cantidad, precio, subtotal, estado, tarifaRango, formulaAplicada, esFacturado, usuario)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, %s)
                """
                vals_ins = (id_cliente, codigo_producto, f_desde, f_hasta, balance, cantidad, precio, subtotal, estado, tarifa_rango, formula_aplicada, usuario)
                res_db = db.ejecutar(sql_ins, vals_ins)

                if res_db == 'ok':
                    # Registrar Auditoría (RF 15, RF 17)
                    db.ejecutar("""
                        INSERT INTO auditoria_periodos (idPeriodo, accion, balanceNuevo, precioNuevo, motivo, usuario)
                        VALUES (LAST_INSERT_ID(), 'CREACION', %s, %s, %s, %s)
                    """, (balance, precio, f"Nuevo período {desde_str} a {hasta_str}", usuario))
                    return {"ok": True, "msg": "Período registrado exitosamente.", "calculo": calc}
                else:
                    return {"ok": False, "msg": res_db}
            else:
                # Modificación autorizada
                sql_upd = """
                    UPDATE periodos_actividades_economicas
                    SET codigoProducto=%s, desde=%s, hasta=%s, balance=%s, precio=%s, subtotal=%s, tarifaRango=%s, formulaAplicada=%s, usuario=%s
                    WHERE idPeriodo=%s
                """
                vals_upd = (codigo_producto, f_desde, f_hasta, balance, precio, subtotal, tarifa_rango, formula_aplicada, usuario, id_periodo)
                res_db = db.ejecutar(sql_upd, vals_upd)
                if res_db == 'ok':
                    db.ejecutar("""
                        INSERT INTO auditoria_periodos (idPeriodo, accion, balanceNuevo, precioNuevo, motivo, usuario)
                        VALUES (%s, 'MODIFICACION', %s, %s, 'Actualización autorizada de balance/período', %s)
                    """, (id_periodo, balance, precio, usuario))
                    return {"ok": True, "msg": "Período actualizado exitosamente.", "calculo": calc}
                else:
                    return {"ok": False, "msg": res_db}

        except Exception as e:
            return {"ok": False, "msg": f"Error interno: {str(e)}"}
