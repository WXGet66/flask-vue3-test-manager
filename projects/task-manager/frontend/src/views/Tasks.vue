<template>
  <el-container>
    <el-header>
      <el-row justify="space-between" align="middle">
        <h2>任务管理</h2>
        <el-dropdown @command="handleCommand">
          <span class="user-info">{{ userStore.userInfo?.username }}</span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人信息</el-dropdown-item>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-row>
    </el-header>
    <el-main>
      <!-- 工具栏 -->
      <el-row :gutter="20" class="toolbar">
        <el-col :span="6">
          <el-select v-model="filter.completed" placeholder="全部" clearable @change="fetchTasks">
            <el-option label="全部" :value="undefined" />
            <el-option label="已完成" :value="true" />
            <el-option label="未完成" :value="false" />
          </el-select>
        </el-col>
        <el-col :span="18" style="text-align: right">
          <el-button type="primary" @click="openCreateDialog">新增任务</el-button>
          <el-button @click="sendRemind">发送提醒邮件</el-button>
          <el-button @click="handleTestEmail">测试邮件</el-button>   <!-- 修改点1：@click 改为 handleTestEmail -->
        </el-col>
      </el-row>

      <!-- 任务列表 -->
      <el-table :data="tasks" style="width: 100%">
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="completed" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.completed ? 'success' : 'info'">
              {{ row.completed ? '已完成' : '未完成' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="due_date" label="截止日期" width="150">
          <template #default="{ row }">{{ formatDate(row.due_date) }}</template>
        </el-table-column>
        <el-table-column label="标签" width="150">
          <template #default="{ row }">
            <el-tag v-for="tag in row.tags" :key="tag.id" size="small" style="margin-right: 4px">
              {{ tag.name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 任务编辑对话框 -->
      <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
        <el-form :model="taskForm" :rules="taskRules" ref="taskFormRef">
          <el-form-item label="标题" prop="title">
            <el-input v-model="taskForm.title" />
          </el-form-item>
          <el-form-item label="描述" prop="description">
            <el-input v-model="taskForm.description" type="textarea" />
          </el-form-item>
          <el-form-item label="截止日期" prop="due_date">
            <el-date-picker v-model="taskForm.due_date" type="datetime" placeholder="选择日期时间" format="YYYY-MM-DD HH:mm" />
          </el-form-item>
          <el-form-item label="状态" prop="completed">
            <el-switch v-model="taskForm.completed" :active-value="true" :inactive-value="false" />
          </el-form-item>
          <el-form-item label="标签" prop="tag_ids">
            <el-select v-model="taskForm.tag_ids" multiple placeholder="请选择标签">
              <el-option v-for="tag in tags" :key="tag.id" :label="tag.name" :value="tag.id" />
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveTask" :loading="saving">保存</el-button>
        </template>
      </el-dialog>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '../stores/user'
import { getTasks, createTask, updateTask, deleteTask, remindTasks, testEmail } from '../api/tasks'  // 导入 testEmail
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import request from '../api/request' // 用于获取标签

const userStore = useUserStore()
const router = useRouter()
const tasks = ref([])
const tags = ref([])
const filter = ref({ completed: undefined })
const dialogVisible = ref(false)
const dialogTitle = ref('新增任务')
const taskForm = ref({ title: '', description: '', due_date: null, completed: false, tag_ids: [] })
const taskFormRef = ref(null)
const saving = ref(false)
const currentEditId = ref(null)

const taskRules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
}

// 获取任务列表
const fetchTasks = async () => {
  const params = {}
  if (filter.value.completed !== undefined) {
    params.completed = filter.value.completed
  }
  const res = await getTasks(params)
  if (res.data.code === 200) {
    tasks.value = res.data.data
  }
}

// 获取标签列表
const fetchTags = async () => {
  const res = await request.get('/tags/')
  if (res.data.code === 200) {
    tags.value = res.data.data
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString()
}

const openCreateDialog = () => {
  dialogTitle.value = '新增任务'
  taskForm.value = { title: '', description: '', due_date: null, completed: false, tag_ids: [] }
  currentEditId.value = null
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  dialogTitle.value = '编辑任务'
  taskForm.value = {
    title: row.title,
    description: row.description,
    due_date: row.due_date,
    completed: row.completed,
    tag_ids: row.tags.map(t => t.id)
  }
  currentEditId.value = row.id
  dialogVisible.value = true
}

const saveTask = async () => {
  await taskFormRef.value.validate()
  saving.value = true
  try {
    if (currentEditId.value) {
      await updateTask(currentEditId.value, taskForm.value)
      ElMessage.success('更新成功')
    } else {
      await createTask(taskForm.value)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    fetchTasks()
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    saving.value = false
  }
}

const handleDelete = (id) => {
  ElMessageBox.confirm('确定删除该任务吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    await deleteTask(id)
    ElMessage.success('删除成功')
    fetchTasks()
  }).catch(() => {})
}

const sendRemind = async () => {
  try {
    const res = await remindTasks()
    if (res.data.code === 200) {
      ElMessage.success(res.data.msg)
    } else {
      ElMessage.warning(res.data.msg)
    }
  } catch (error) {
    ElMessage.error('发送失败')
  }
}

// 修改点2：将本地函数重命名为 handleTestEmail
const handleTestEmail = async () => {
  try {
    const res = await testEmail()   // 调用导入的 testEmail
    if (res.data.code === 200) {
      ElMessage.success(res.data.msg)
    } else {
      ElMessage.error(res.data.msg)
    }
  } catch (error) {
    ElMessage.error('测试邮件发送失败')
  }
}

const handleCommand = (cmd) => {
  if (cmd === 'logout') {
    userStore.logout()
    router.push('/login')
  } else if (cmd === 'profile') {
    ElMessage.info('个人信息功能待实现')
  }
}

onMounted(() => {
  fetchTasks()
  fetchTags()
})
</script>

<style scoped>
.el-header {
  border-bottom: 1px solid #eee;
  line-height: 60px;
}
.user-info {
  cursor: pointer;
}
.toolbar {
  margin-bottom: 20px;
}
</style>