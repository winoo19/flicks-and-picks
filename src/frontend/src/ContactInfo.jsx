import './index.css'

function QuestionForm({ question }) {
    return <>
        <div class="form-control">
            <label for={question}>{question}</label>
            <input type="text" placeholder="Nombre" required />
        </div>
    </>
}

function Form() {
    return <>
        <form action="" method="post">
            <QuestionForm question={"Nombre"} />
            <QuestionForm question={"Email"} />
            <QuestionForm question={"Asunto"} />
            <div className="form-control">
                <label for="message">Mensaje</label>
                <textarea name="message" placeholder="Mensaje"></textarea>
            </div>

            <button type="submit">Enviar</button>
        </form>
    </>
}

function Inicio() {
    return <>
        <h2 id="title"></h2>
        <p>Somos una tienda fundada en 2024 dedicada a la venta minorista de productos tecnológicos a buen precio.</p>
        <p>Nuestro teléfono de atención al cliente es 91606066 de 8h a 19h de lunes a viernes.</p>
        <p>Pero también puedes contactarnos a cualquier hora con el siguiente formulario.</p>
    </>
}


function Info() {
    return <>
        <div className="info">
            <Inicio />
            <Form />
        </div>
    </>
}


function DetailsPage() {
    return <>
        <div className="container">
            <h2>¿Quiénes somos?</h2>
            <Info />
        </div>

    </>
}

function ContactInfo() {
    return (
        <>
            <DetailsPage />
        </>
    )
}

export default ContactInfo
