import { onActivated, onMounted, ref } from 'vue'

export type RefreshLoadOptions = { silent?: boolean }

/**
 * KeepAlive 缓存的列表页：从添加/编辑子路由返回时静默刷新。
 * 首次挂载只执行 onMountLoad；onActivated 跳过第一次（与 onMounted 重复）。
 */
export function useRefreshOnActivate(
  onMountLoad: () => void | Promise<void>,
  onActivateLoad: (options: RefreshLoadOptions) => void | Promise<void>,
): void {
  const skipNextActivate = ref(true)

  onMounted(() => {
    void onMountLoad()
  })

  onActivated(() => {
    if (skipNextActivate.value) {
      skipNextActivate.value = false
      return
    }
    void onActivateLoad({ silent: true })
  })
}
