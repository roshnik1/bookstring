/**
 * Documentation page for the python / FastAPI server
 */

import { useEffect, useState } from "react"

import { xml2js, type Element } from "xml-js"
import { SERVER_URL } from "../../common"


export default function ServerDevdocs() {
  const [document, setDocument] = useState<Element|null>(null)

  useEffect(() => {
    console.log("getting xml doc")
    fetch(`${SERVER_URL}dev/docs/server`).then(async (response) => {
      console.log("got response")
      const content = await response.text()
      setDocument(xml2js(content, {compact: false}).elements[0] as Element)
    })
  }, [])

  if (document === null) {
    return <h1>Loading...</h1>
  } else if (document.name !== "module") {
    console.error(document)
    return <h1>Unexpected root node '{document.name}'</h1>
  }

  return (
    <>
      <section id="center">
        <ModuleElement element={document} nesting={0} />
      </section>
    </>
  )
}


type ElementProps = {
  element: Element
  nesting: number
}

function ModuleElement({ element, nesting }: ElementProps) {
  const docElm: Element|undefined = element.elements.find((elm) => elm.name == "doc")

  return (
    <div className="dev pydoc module">
      <h1>Module <span className="dev pydoc name">{element.attributes["name"]}</span></h1>
      {docElm && <DocumentElement element={docElm} nesting={nesting+1} />}
      {element.elements.map((chelm) => {
        switch (chelm.name) {
          case "file":
            return <span>{chelm.attributes["name"]}</span>
          case "module":
            return <ModuleElement element={chelm} nesting={nesting+1} />
          default:
            return <></>
        }
      })}
    </div>
  )
}


function DocumentElement({ element }: ElementProps) {
  return (<></>)
}