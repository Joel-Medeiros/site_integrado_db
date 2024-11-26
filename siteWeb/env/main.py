from flask import Flask, render_template, request,redirect,flash
import mysql.connector


app = Flask(__name__)
app.secret_key = 'sua-chave-secreta'


def get_db_connection():
    return mysql.connector.connect(
        host="***.**.*.**",
        user="usr_aluno",
        password="***********",
        database="aula_fatec",
        port=5000
    )


@app.route("/")
def home():
    return render_template("base.html")


#
@app.route("/disciplinas", methods=["GET", "POST"])
def disciplinas():
    db = get_db_connection()
    cursor = db.cursor()

    search_term = request.args.get('search', '')

    if search_term:
        cursor.execute("SELECT * FROM joel_disciplina WHERE nome LIKE %s OR id LIKE %s",
                       ('%' + search_term + '%', '%' + search_term + '%'))
    else:
        cursor.execute("SELECT * FROM joel_disciplina")

    disciplinas = cursor.fetchall()
    db.close()

    return render_template("disciplinas.html", disciplinas=disciplinas)


@app.route("/disciplinas/inserir", methods=["GET", "POST"])
def inserir_disciplina():
    if request.method == "POST":
        try:
            nome = request.form["nome"]
            carga_horaria = request.form["carga_horaria"]
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("INSERT INTO joel_disciplina (nome, carga_horaria) VALUES (%s, %s)", (nome, carga_horaria))
            db.commit()
            db.close()
            flash("Disciplina inserida com sucesso!", "success")
        except Exception as e:
            flash(f"Erro ao inserir disciplina: {e}", "error")
        return redirect("/disciplinas")
    return render_template("inserir_disciplina.html")


@app.route("/disciplinas/editar/<int:id>", methods=["GET", "POST"])
def editar_disciplina(id):
    db = get_db_connection()
    cursor = db.cursor()

    if request.method == "POST":
        try:
            nome = request.form["nome"]
            carga_horaria = request.form["carga_horaria"]
            cursor.execute("UPDATE joel_disciplina SET nome = %s, carga_horaria = %s WHERE id = %s", (nome, carga_horaria, id))
            db.commit()
            flash("Disciplina atualizada com sucesso!", "success")
        except Exception as e:
            flash(f"Erro ao atualizar disciplina: {e}", "error")
        finally:
            db.close()
        return redirect("/disciplinas")

    cursor.execute("SELECT * FROM joel_disciplina WHERE id = %s", (id,))
    disciplina = cursor.fetchone()
    db.close()

    if not disciplina:
        flash("Disciplina não encontrada!", "error")
        return redirect("/disciplinas")

    return render_template("editar_disciplina.html", disciplina=disciplina)


@app.route("/disciplinas/excluir/<int:id>", methods=["POST"])
def excluir_disciplina(id):
    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute("DELETE FROM joel_disciplina WHERE id = %s", (id,))
        db.commit()
        flash("Disciplina excluída com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao excluir disciplina: {e}", "error")
    finally:
        db.close()

    return redirect("/disciplinas")

#########################################################################33

@app.route("/cursos", methods=["GET"]) 
def cursos():
    db = get_db_connection()
    cursor = db.cursor()
    
    
    search_term = request.args.get('search', '')  
    
    
    if search_term:
        cursor.execute("""
            SELECT c.id, c.nome, c.carga_horaria_total, GROUP_CONCAT(d.nome ORDER BY d.nome ASC) AS disciplinas
            FROM joel_curso c
            LEFT JOIN joel_curso_disciplina cd ON c.id = cd.curso_id
            LEFT JOIN joel_disciplina d ON cd.disciplina_id = d.id
            WHERE c.nome LIKE %s OR d.nome LIKE %s
            GROUP BY c.id
        """, ('%' + search_term + '%', '%' + search_term + '%'))
    else:
        
        cursor.execute("""
            SELECT c.id, c.nome, c.carga_horaria_total, GROUP_CONCAT(d.nome ORDER BY d.nome ASC) AS disciplinas
            FROM joel_curso c
            LEFT JOIN joel_curso_disciplina cd ON c.id = cd.curso_id
            LEFT JOIN joel_disciplina d ON cd.disciplina_id = d.id
            GROUP BY c.id
        """)
    
    cursos = cursor.fetchall()
    db.close()
    
    return render_template("cursos.html", cursos=cursos)


@app.route("/cursos/inserir", methods=["GET", "POST"])
def inserir_curso():
    db = get_db_connection()
    cursor = db.cursor()
    
    if request.method == "POST":
        try:
            nome = request.form["nome"]
            disciplinas_selecionadas = request.form.getlist("disciplinas")  
            carga_horaria_total = 0

            
            for disciplina_id in disciplinas_selecionadas:
                cursor.execute("SELECT carga_horaria FROM joel_disciplina WHERE id = %s", (disciplina_id,))
                carga_horaria = cursor.fetchone()
                if carga_horaria:
                    carga_horaria_total += carga_horaria[0]

            
            cursor.execute("INSERT INTO joel_curso (nome, carga_horaria_total) VALUES (%s, %s)", (nome, carga_horaria_total))
            curso_id = cursor.lastrowid  

            
            for disciplina_id in disciplinas_selecionadas:
                cursor.execute("INSERT INTO joel_curso_disciplina (curso_id, disciplina_id) VALUES (%s, %s)", (curso_id, disciplina_id))
            
            db.commit()
            flash("Curso inserido com sucesso!", "success")
        except Exception as e:
            flash(f"Erro ao inserir curso: {e}", "error")
        finally:
            db.close()
        
        return redirect("/cursos")
    
   
    cursor.execute("SELECT * FROM joel_disciplina")
    disciplinas = cursor.fetchall()
    db.close()
    
    return render_template("inserir_curso.html", disciplinas=disciplinas)


@app.route("/cursos/editar/<int:id>", methods=["GET", "POST"])
def editar_curso(id):
    db = get_db_connection()
    cursor = db.cursor()
    
    
    cursor.execute("SELECT * FROM joel_curso WHERE id = %s", (id,))
    curso = cursor.fetchone()
    
    if not curso:
        flash("Curso não encontrado!", "error")
        db.close()
        return redirect("/cursos")
    
    if request.method == "POST":
        try:
            nome = request.form["nome"]
            disciplinas_selecionadas = request.form.getlist("disciplinas")  
            carga_horaria_total = 0

            
            for disciplina_id in disciplinas_selecionadas:
                cursor.execute("SELECT carga_horaria FROM joel_disciplina WHERE id = %s", (disciplina_id,))
                carga_horaria = cursor.fetchone()
                if carga_horaria:
                    carga_horaria_total += carga_horaria[0]

           
            cursor.execute("UPDATE joel_curso SET nome = %s, carga_horaria_total = %s WHERE id = %s", 
                           (nome, carga_horaria_total, id))

            
            cursor.execute("DELETE FROM joel_curso_disciplina WHERE curso_id = %s", (id,))

           
            for disciplina_id in disciplinas_selecionadas:
                cursor.execute("INSERT INTO joel_curso_disciplina (curso_id, disciplina_id) VALUES (%s, %s)", (id, disciplina_id))
            
            db.commit()
            flash("Curso atualizado com sucesso!", "success")
        except Exception as e:
            flash(f"Erro ao atualizar curso: {e}", "error")
        finally:
            db.close()

        return redirect("/cursos")
    
    
    cursor.execute("SELECT * FROM joel_disciplina")
    disciplinas = cursor.fetchall()
    
    
    cursor.execute("SELECT disciplina_id FROM joel_curso_disciplina WHERE curso_id = %s", (id,))
    disciplinas_associadas = [disciplina[0] for disciplina in cursor.fetchall()]
    
    db.close()

    return render_template("editar_curso.html", curso=curso, disciplinas=disciplinas, disciplinas_associadas=disciplinas_associadas)


@app.route("/cursos/excluir/<int:id>", methods=["POST"])
def excluir_curso(id):
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        
        cursor.execute("DELETE FROM joel_curso_disciplina WHERE curso_id = %s", (id,))
        
        
        cursor.execute("DELETE FROM joel_curso WHERE id = %s", (id,))
        
        db.commit()
        flash("Curso excluído com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao excluir curso: {e}", "error")
    finally:
        db.close()

    return redirect("/cursos")

    ###################################################
@app.route("/professores", methods=["GET"])
def professores():
    db = get_db_connection()
    cursor = db.cursor()

    # Captura o termo de busca
    busca = request.args.get("busca", "")

    if busca:
        
        cursor.execute("""
            SELECT p.id, p.nome, p.telefone, p.usuario_login, GROUP_CONCAT(d.nome ORDER BY d.nome ASC) AS disciplinas
            FROM joel_professor p
            LEFT JOIN joel_professor_disciplina pd ON p.id = pd.professor_id
            LEFT JOIN joel_disciplina d ON pd.disciplina_id = d.id
            WHERE p.nome LIKE %s
            GROUP BY p.id
        """, ('%' + busca + '%',))
    else:
       
        cursor.execute("""
            SELECT p.id, p.nome, p.telefone, p.usuario_login, GROUP_CONCAT(d.nome ORDER BY d.nome ASC) AS disciplinas
            FROM joel_professor p
            LEFT JOIN joel_professor_disciplina pd ON p.id = pd.professor_id
            LEFT JOIN joel_disciplina d ON pd.disciplina_id = d.id
            GROUP BY p.id
        """)

    professores = cursor.fetchall()
    db.close()

    return render_template("professores.html", professores=professores, busca=busca)

@app.route("/professores", methods=["GET"])
def listar_professores():
    db = get_db_connection()
    cursor = db.cursor()

    # Captura o termo de busca
    busca = request.args.get("busca", "")

    if busca:
        
        cursor.execute("""
            SELECT p.id, p.nome, p.telefone, p.usuario_login, GROUP_CONCAT(d.nome) AS disciplinas
            FROM joel_professores p
            LEFT JOIN joel_professor_disciplina pd ON p.id = pd.professor_id
            LEFT JOIN joel_disciplinas d ON pd.disciplina_id = d.id
            WHERE p.nome LIKE %s
            GROUP BY p.id
        """, ('%' + busca + '%',))
    else:
        
        cursor.execute("""
            SELECT p.id, p.nome, p.telefone, p.usuario_login, GROUP_CONCAT(d.nome) AS disciplinas
            FROM joel_professores p
            LEFT JOIN joel_professor_disciplina pd ON p.id = pd.professor_id
            LEFT JOIN joel_disciplinas d ON pd.disciplina_id = d.id
            GROUP BY p.id
        """)

    professores = cursor.fetchall()
    db.close()

    return render_template("listar_professores.html", professores=professores)

@app.route("/professores/inserir", methods=["GET", "POST"])
def inserir_professor():
    db = get_db_connection()
    cursor = db.cursor()

    if request.method == "POST":
        try:
            nome = request.form["nome"]
            telefone = request.form["telefone"]
            usuario_login = request.form["usuario_login"]
            senha = request.form["senha"] 
            disciplinas = request.form.getlist("disciplinas")

            
            cursor.execute("""
                INSERT INTO joel_professor (nome, telefone, usuario_login, senha)
                VALUES (%s, %s, %s, %s)
            """, (nome, telefone, usuario_login, senha))
            professor_id = cursor.lastrowid

           
            for disciplina_id in disciplinas:
                cursor.execute("""
                    INSERT INTO joel_professor_disciplina (professor_id, disciplina_id)
                    VALUES (%s, %s)
                """, (professor_id, disciplina_id))

            db.commit()
            flash("Professor cadastrado com sucesso!", "success")
        except Exception as e:
            db.rollback()
            flash(f"Erro ao inserir professor: {e}", "danger")
        finally:
            db.close()
        return redirect("/professores")

    
    cursor.execute("SELECT id, nome FROM joel_disciplina")
    disciplinas = cursor.fetchall()

    db.close()

    return render_template("inserir_professor.html", disciplinas=disciplinas)

@app.route("/professores/editar/<int:id>", methods=["GET", "POST"])
def editar_professor(id):
    db = get_db_connection()
    cursor = db.cursor()
    
    
    cursor.execute("SELECT * FROM joel_professor WHERE id = %s", (id,))
    professor = cursor.fetchone()
    
    if not professor:
        flash("Professor não encontrado!", "error")
        db.close()
        return redirect("/professores")
    
    if request.method == "POST":
        try:
            nome = request.form["nome"]
            telefone = request.form["telefone"]
            usuario_login = request.form["usuario_login"]
            senha = request.form["senha"]
            disciplinas_selecionadas = request.form.getlist("disciplinas")

           
            cursor.execute("UPDATE joel_professor SET nome = %s, telefone = %s, usuario_login = %s, senha = %s WHERE id = %s", 
                           (nome, telefone, usuario_login, senha, id))

            
            cursor.execute("DELETE FROM joel_professor_disciplina WHERE professor_id = %s", (id,))

           
            for disciplina_id in disciplinas_selecionadas:
                cursor.execute("INSERT INTO joel_professor_disciplina (professor_id, disciplina_id) VALUES (%s, %s)", (id, disciplina_id))
            
            db.commit()
            flash("Professor atualizado com sucesso!", "success")
        except Exception as e:
            flash(f"Erro ao atualizar professor: {e}", "error")
        finally:
            db.close()

        return redirect("/professores")
    
    
    cursor.execute("SELECT * FROM joel_disciplina")
    disciplinas = cursor.fetchall()

    
    cursor.execute("SELECT disciplina_id FROM joel_professor_disciplina WHERE professor_id = %s", (id,))
    disciplinas_associadas = [disciplina[0] for disciplina in cursor.fetchall()]
    
    db.close()

    return render_template("editar_professor.html", professor=professor, disciplinas=disciplinas, disciplinas_associadas=disciplinas_associadas)

@app.route("/professores/excluir/<int:id>", methods=["POST"])
def excluir_professor(id):
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        
        cursor.execute("DELETE FROM joel_professor_disciplina WHERE professor_id = %s", (id,))
        
        
        cursor.execute("DELETE FROM joel_professor WHERE id = %s", (id,))
        
        db.commit()
        flash("Professor excluído com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao excluir professor: {e}", "error")
    finally:
        db.close()

    return redirect("/professores")


    ################################################

@app.route("/alunos", methods=["GET"])
def listar_alunos():
    db = get_db_connection()
    cursor = db.cursor()

  
    busca = request.args.get("busca", "")

    if busca:
        
        cursor.execute("""
            SELECT a.id, a.nome, a.cpf, a.endereco,  c.nome AS curso
            FROM joel_aluno a
            LEFT JOIN joel_aluno_curso ac ON a.id = ac.aluno_id
            LEFT JOIN joel_curso c ON ac.curso_id = c.id
            WHERE a.nome LIKE %s
            GROUP BY a.id, c.nome  # Adiciona c.nome no GROUP BY
        """, ('%' + busca + '%',))
    else:
        
        cursor.execute("""
            SELECT a.id, a.nome, a.cpf, a.endereco,  c.nome AS curso
            FROM joel_aluno a
            LEFT JOIN joel_aluno_curso ac ON a.id = ac.aluno_id
            LEFT JOIN joel_curso c ON ac.curso_id = c.id
            GROUP BY a.id, c.nome  # Adiciona c.nome no GROUP BY
        """)

    alunos = cursor.fetchall()
    db.close()

    return render_template("listar_alunos.html", alunos=alunos)


@app.route("/alunos/inserir", methods=["GET", "POST"])
def inserir_aluno():
    db = get_db_connection()
    cursor = db.cursor()

    if request.method == "POST":
        try:
            nome = request.form["nome"]
            cpf = request.form["cpf"]
            endereco = request.form["endereco"]
            usuario_login = request.form["usuario_login"]
            senha = request.form["senha"] 
            curso = request.form["curso"]

            
            cursor.execute("""
                INSERT INTO joel_aluno (nome, cpf, endereco, usuario_login, senha)
                VALUES (%s, %s, %s, %s, %s)
            """, (nome, cpf, endereco, usuario_login, senha))
            aluno_id = cursor.lastrowid

           
            cursor.execute("""
                INSERT INTO joel_aluno_curso (aluno_id, curso_id)
                VALUES (%s, %s)
            """, (aluno_id, curso))

            db.commit()
            flash("Aluno cadastrado com sucesso!", "success")
        except Exception as e:
            db.rollback()
            flash(f"Erro ao inserir aluno: {e}", "danger")
        finally:
            db.close()

        return redirect("/alunos")

   
    cursor.execute("SELECT id, nome FROM joel_curso")
    cursos = cursor.fetchall()

    db.close()

    return render_template("inserir_aluno.html", cursos=cursos)

@app.route("/alunos/editar/<int:id>", methods=["GET", "POST"])
def editar_aluno(id):
    db = get_db_connection()
    cursor = db.cursor()

    
    cursor.execute("SELECT * FROM joel_aluno WHERE id = %s", (id,))
    aluno = cursor.fetchone()

    if not aluno:
        flash("Aluno não encontrado!", "error")
        db.close()
        return redirect("/alunos")

    if request.method == "POST":
        try:
            nome = request.form["nome"]
            cpf = request.form["cpf"]
            endereco = request.form["endereco"]
            usuario_login = request.form["usuario_login"]
            senha = request.form["senha"]
            curso_selecionado = request.form["curso"]

            
            cursor.execute("""
                UPDATE joel_aluno SET nome = %s, cpf = %s, endereco = %s, usuario_login = %s, senha = %s
                WHERE id = %s
            """, (nome, cpf, endereco, usuario_login, senha, id))

            
            cursor.execute("DELETE FROM joel_aluno_curso WHERE aluno_id = %s", (id,))

            
            cursor.execute("""
                INSERT INTO joel_aluno_curso (aluno_id, curso_id)
                VALUES (%s, %s)
            """, (id, curso_selecionado))

            db.commit()
            flash("Aluno atualizado com sucesso!", "success")
        except Exception as e:
            flash(f"Erro ao atualizar aluno: {e}", "error")
        finally:
            db.close()

        return redirect("/alunos")

   
    cursor.execute("SELECT * FROM joel_curso")
    cursos = cursor.fetchall()

   
    cursor.execute("SELECT curso_id FROM joel_aluno_curso WHERE aluno_id = %s", (id,))
    curso_associado = cursor.fetchone()[0]

    db.close()

    return render_template("editar_aluno.html", aluno=aluno, cursos=cursos, curso_associado=curso_associado)

@app.route("/alunos/excluir/<int:id>", methods=["POST"])
def excluir_aluno(id):
    db = get_db_connection()
    cursor = db.cursor()

    try:
        
        cursor.execute("DELETE FROM joel_aluno_curso WHERE aluno_id = %s", (id,))

       
        cursor.execute("DELETE FROM joel_aluno WHERE id = %s", (id,))

        db.commit()
        flash("Aluno excluído com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao excluir aluno: {e}", "error")
    finally:
        db.close()

    return redirect("/alunos")

if __name__ == "__main__":
    app.run(debug=True)

