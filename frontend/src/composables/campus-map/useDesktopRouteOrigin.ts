import { ref, type ComputedRef } from 'vue'
import type { CampusPlace } from '../../components/campus-map/types'

interface DesktopRouteOriginOptions {
  isDesktop: ComputedRef<boolean>
  hasOrigin: ComputedRef<boolean>
  profileDormLabel: ComputedRef<string | null>
  locateAtProfileDorm: () => boolean
  locateMyPosition: () => Promise<boolean>
  setPlaceAsOrigin: (place: CampusPlace) => boolean
  planRoute: (place: CampusPlace) => void
  onMobileMissing: () => void
  getGeoMessage: () => string
}

export function useDesktopRouteOrigin(options: DesktopRouteOriginOptions) {
  const promptOpen = ref(false)
  const promptMessage = ref('导航需要先设置起点，请选择一种方式')
  const choosingOrigin = ref(false)
  const pendingTarget = ref<CampusPlace | null>(null)

  function finishOriginChoice(success: boolean) {
    if (!success) return false
    promptOpen.value = false
    choosingOrigin.value = false
    const target = pendingTarget.value
    pendingTarget.value = null
    if (target) options.planRoute(target)
    return true
  }

  function requestRoute(target: CampusPlace) {
    if (options.hasOrigin.value) {
      options.planRoute(target)
      return
    }
    if (!options.isDesktop.value) {
      pendingTarget.value = target
      choosingOrigin.value = true
      promptOpen.value = false
      options.onMobileMissing()
      return
    }
    pendingTarget.value = target
    promptMessage.value = options.profileDormLabel.value
      ? `导航到目的地前，请先设置起点。推荐使用「${options.profileDormLabel.value}」，也可定位当前位置或在地图上手动选点。`
      : '导航到目的地前，请先设置起点：可定位当前位置，或在地图上手动选择当前位置。'
    promptOpen.value = true
  }

  function chooseDorm() {
    finishOriginChoice(options.locateAtProfileDorm())
  }

  async function chooseDevice() {
    const success = await options.locateMyPosition()
    if (finishOriginChoice(success)) return
    promptMessage.value = options.getGeoMessage() || '定位失败，请改用手动选择当前位置或宿舍作为起点'
    promptOpen.value = true
  }

  function beginMapSelection() {
    promptOpen.value = false
    choosingOrigin.value = true
  }

  function useSelectedPlace(place: CampusPlace) {
    if (!choosingOrigin.value) return false
    return finishOriginChoice(options.setPlaceAsOrigin(place))
  }

  function cancelPrompt() {
    promptOpen.value = false
    pendingTarget.value = null
    choosingOrigin.value = false
  }

  return {
    promptOpen,
    promptMessage,
    choosingOrigin,
    pendingTarget,
    requestRoute,
    chooseDorm,
    chooseDevice,
    beginMapSelection,
    useSelectedPlace,
    cancelPrompt,
  }
}
