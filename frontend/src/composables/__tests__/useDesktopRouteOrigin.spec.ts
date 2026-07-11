import { computed, ref } from 'vue'
import { describe, expect, it, vi } from 'vitest'
import { campusPlaces } from '../../components/campus-map/campusPlaces'
import { useDesktopRouteOrigin } from '../campus-map/useDesktopRouteOrigin'

function createHarness(options: {
  desktop?: boolean
  hasOrigin?: boolean
  dorm?: string | null
  deviceSuccess?: boolean
} = {}) {
  const desktop = ref(options.desktop ?? true)
  const hasOrigin = ref(options.hasOrigin ?? false)
  const dorm = ref(options.dorm === undefined ? '学生公寓 5 号楼' : options.dorm)
  const planRoute = vi.fn()
  const locateDorm = vi.fn(() => true)
  const locateDevice = vi.fn(async () => options.deviceSuccess ?? false)
  const setManual = vi.fn(() => true)
  const mobileMissing = vi.fn()
  const flow = useDesktopRouteOrigin({
    isDesktop: computed(() => desktop.value),
    hasOrigin: computed(() => hasOrigin.value),
    profileDormLabel: computed(() => dorm.value),
    locateAtProfileDorm: locateDorm,
    locateMyPosition: locateDevice,
    setPlaceAsOrigin: setManual,
    planRoute,
    onMobileMissing: mobileMissing,
    getGeoMessage: () => '定位权限被拒绝',
  })
  return { flow, planRoute, locateDorm, locateDevice, setManual, mobileMissing }
}

describe('useDesktopRouteOrigin', () => {
  it('opens a desktop origin prompt instead of blocking route planning', () => {
    const { flow, planRoute } = createHarness()
    const target = campusPlaces[0]

    flow.requestRoute(target)

    expect(flow.promptOpen.value).toBe(true)
    expect(flow.pendingTarget.value?.id).toBe(target.id)
    expect(planRoute).not.toHaveBeenCalled()
  })

  it('resumes the pending route after choosing the profile dormitory', () => {
    const { flow, locateDorm, planRoute } = createHarness()
    const target = campusPlaces[0]
    flow.requestRoute(target)

    flow.chooseDorm()

    expect(locateDorm).toHaveBeenCalledOnce()
    expect(planRoute).toHaveBeenCalledWith(target)
    expect(flow.promptOpen.value).toBe(false)
  })

  it('uses the next selected place as a manual origin and resumes the route', () => {
    const { flow, setManual, planRoute } = createHarness({ dorm: null })
    const target = campusPlaces[0]
    const origin = campusPlaces[1]
    flow.requestRoute(target)
    flow.beginMapSelection()

    expect(flow.useSelectedPlace(origin)).toBe(true)
    expect(setManual).toHaveBeenCalledWith(origin)
    expect(planRoute).toHaveBeenCalledWith(target)
  })

  it('starts manual origin selection on mobile when no route origin exists', () => {
    const { flow, mobileMissing, planRoute } = createHarness({ desktop: false })

    flow.requestRoute(campusPlaces[0])

    expect(mobileMissing).toHaveBeenCalledOnce()
    expect(flow.choosingOrigin.value).toBe(true)
    expect(flow.pendingTarget.value?.id).toBe(campusPlaces[0].id)
    expect(planRoute).not.toHaveBeenCalled()
  })

  it('resumes the pending mobile route after choosing a manual map origin', () => {
    const { flow, setManual, planRoute } = createHarness({ desktop: false, dorm: null })
    const target = campusPlaces[0]
    const origin = campusPlaces[2]

    flow.requestRoute(target)

    expect(flow.useSelectedPlace(origin)).toBe(true)
    expect(setManual).toHaveBeenCalledWith(origin)
    expect(planRoute).toHaveBeenCalledWith(target)
  })

  it('plans immediately when a route origin already exists', () => {
    const { flow, planRoute } = createHarness({ hasOrigin: true })
    const target = campusPlaces[0]

    flow.requestRoute(target)

    expect(planRoute).toHaveBeenCalledWith(target)
  })

  it('resumes a pending route after successful device location', async () => {
    const { flow, planRoute } = createHarness({ deviceSuccess: true })
    const target = campusPlaces[0]
    flow.requestRoute(target)

    await flow.chooseDevice()

    expect(planRoute).toHaveBeenCalledWith(target)
    expect(flow.promptOpen.value).toBe(false)
  })

  it('keeps the prompt open with the precise device error after failure', async () => {
    const { flow } = createHarness()
    flow.requestRoute(campusPlaces[0])

    await flow.chooseDevice()

    expect(flow.promptOpen.value).toBe(true)
    expect(flow.promptMessage.value).toBe('定位权限被拒绝')
  })

  it('cancels the prompt and clears the pending destination', () => {
    const { flow } = createHarness()
    flow.requestRoute(campusPlaces[0])

    flow.cancelPrompt()

    expect(flow.promptOpen.value).toBe(false)
    expect(flow.pendingTarget.value).toBeNull()
  })
})
