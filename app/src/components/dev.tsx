/* eslint-disable @typescript-eslint/no-unused-vars */
import { useEffect, useState } from "react"
import type { ReactNode } from "react"
import { SERVER_URL } from "../common"

export function Placeholder(
  { children, name, comment }: {
    children: ReactNode,
    name: string,
    comment: string,
  }) {
  useEffect(() => {
    console.log(`Rendered placeholder '${name}' (${comment})`)
  })

  return (
    <div className={`dev placeholder placeholder-${name}`}>
      {children}
    </div>
  )
}


export function Devbar() {
  const [hmrStatus, setHMRStatus] = useState(!!import.meta.hot)
  const [apiStatus, setAPIStatus] = useState(false)

  useEffect(() => {
    /** HMR status checking */
    import.meta.hot.on("vite:ws:connect", () => {
      setHMRStatus(true)
      console.log("connected")
    })
    import.meta.hot.on("vite:ws:disconnect", () => {
      setHMRStatus(false)
      console.log("disconnected")
    })

    /** API server status checking */
    setInterval(
      () => {
        fetch(SERVER_URL, { signal: AbortSignal.timeout(1000) })
          .then((_) => {
            setAPIStatus(true)
          })
          .catch((_) => {
            setAPIStatus(false)
          })
      },
      5000
    )
  }, [])

  return (
    <div className="dev devbar">
      <h3>DEVELOPMENT BUILD (v{__PROJECT__.version})</h3>
      <ul>
        <li>branch: <span className="info">{__PROJECT__.branch}</span></li>
        <li>last-commit: <span className="info">{__PROJECT__.commit_hash}</span></li>
        <li>hmr: {
          hmrStatus ? (<span className="good">on</span>) : (<span className="bad">off</span>)
        }</li>
        <li>
          server: <span className="info">port {__CONFIG__.ports.server} </span>
          {(apiStatus) ? <span className="good">up</span> : <span className="bad">down</span>}
        </li>
      </ul>
    </div>
  )
}


export function ErrorBound(
  { children }: {
    children: ReactNode,
  }) {
    return (
      <>
        {children}
      </>
    )
  }