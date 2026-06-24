import { CampusPage } from "./campus/CampusPage"

export default function App() {
  return (
    <CampusPage
      onExit={() => {
        if (window.parent !== window) {
          window.parent.postMessage({ type: "campus:exit" }, window.location.origin)
          return
        }

        // 独立部署：退出回到首页
        if (window.history.length > 1) {
          window.history.back()
        } else {
          window.location.href = "/"
        }
      }}
    />
  )
}
