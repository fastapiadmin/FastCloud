import request from '@/axios'
import type { UserForm, UserTable, UserQuery, UserLoginType } from './types'
import { useUserStoreWithOut } from '@/store/modules/user'

// 用户登录
export const login = async (data: UserLoginType): Promise<IResponse<LoginResponse>> => {
  try {
    const response = await request.post({
      url: '/login',
      data: data,
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    // 保存token到user store
    const userStore = useUserStoreWithOut()
    if (response.data && response.data.access_token) {
      userStore.setToken(response.data.access_token)
    }
    return response
  } catch (error) {
    console.error('登录失败:', error)
    throw error
  }
}

// 用户注销
export const logout = async (): Promise<IResponse> => {
  try {
    const response = await request.post({ url: '/logout' })
    // 清除user store中的token
    const userStore = useUserStoreWithOut()
    userStore.logout()
    return response
  } catch (error) {
    console.error('注销失败:', error)
    // 即使API调用失败，也清除本地token
    const userStore = useUserStoreWithOut()
    userStore.logout()
    throw error
  }
}

// 获取用户列表
export const getUserList = async (
  params?: UserQuery
): Promise<IResponse<PageResponse<UserTable>>> => {
  return await request.get({
    url: '/api/users',
    params
  })
}

// 获取用户详情
export const getUserDetail = async (userId: number): Promise<IResponse<UserTable>> => {
  return await request.get({
    url: `/api/user/${userId}`
  })
}

// 创建用户
export const createUser = async (userData: UserForm): Promise<IResponse<UserTable>> => {
  return await request.post({
    url: '/api/user',
    data: userData
  })
}

// 更新用户
export const updateUser = async (
  userId: number,
  userData: UserForm
): Promise<IResponse<UserTable>> => {
  return await request.put({
    url: `/api/user/${userId}`,
    data: userData
  })
}

// 删除用户
export const deleteUser = async (userId: number): Promise<IResponse> => {
  return await request.delete({
    url: `/api/user/${userId}`
  })
}
