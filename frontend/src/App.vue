<template>
  <div class="min-h-screen p-6 sm:p-10">
    <Toast />
    <header class="mb-8 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-3xl font-bold text-slate-900">Fullstack RAG COM</h1>
        <p class="text-slate-600">Consulta procedimientos por cliente con contexto trazable.</p>
      </div>
      <div class="flex gap-2 text-sm text-slate-500">
        <i class="pi pi-shield text-amber-500"></i>
        <span>Operaciones seguras y auditables</span>
      </div>
    </header>

    <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <Card class="lg:col-span-2 shadow-sm">
        <template #title>
          <div class="flex items-center gap-2">
            <i class="pi pi-comments text-primary-500"></i>
            <span>Consulta RAG</span>
          </div>
        </template>
        <template #content>
          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div class="flex flex-col gap-2">
              <label class="text-sm font-medium text-slate-700">Cliente</label>
              <Dropdown
                v-model="selectedClient"
                :options="clients"
                optionLabel="label"
                optionValue="value"
                placeholder="Selecciona un cliente"
                class="w-full"
              />
            </div>
            <div class="flex flex-col gap-2">
              <label class="text-sm font-medium text-slate-700">Pregunta</label>
              <Textarea
                v-model="question"
                autoResize
                rows="3"
                class="w-full"
                placeholder="Ej: ¿Cuál es el horario de mantenimiento de ACME?"
              />
            </div>
          </div>
          <div class="mt-4 flex flex-wrap gap-3">
            <Button
              label="Consultar"
              icon="pi pi-send"
              :loading="loading"
              :disabled="!canSubmit"
              @click="submitQuery"
            />
            <Button label="Limpiar" icon="pi pi-trash" severity="secondary" outlined @click="clearAll" />
          </div>

          <Divider class="my-6" />

          <div v-if="loading" class="flex items-center gap-3 text-slate-600">
            <ProgressSpinner style="width: 32px; height: 32px" strokeWidth="6" />
            <span>Generando respuesta...</span>
          </div>

          <div v-else>
            <div v-if="answer" class="space-y-4">
              <div>
                <h2 class="mb-2 text-xl font-semibold text-slate-800">Respuesta</h2>
                <p class="rounded-lg bg-slate-100 p-4 leading-relaxed">{{ answer }}</p>
              </div>
              <div>
                <h3 class="mb-2 text-lg font-semibold text-slate-800">Fragmentos utilizados</h3>
                <div class="space-y-3">
                  <Card v-for="(chunk, idx) in chunks" :key="idx" class="border border-slate-100 shadow-none">
                    <template #title>
                      <div class="flex items-center gap-2 text-sm text-slate-500">
                        <Tag :value="chunk.source" severity="info" />
                        <span>Página: {{ chunk.page }}</span>
                      </div>
                    </template>
                    <template #content>
                      <p class="whitespace-pre-line leading-relaxed text-slate-800">{{ chunk.text }}</p>
                    </template>
                  </Card>
                </div>
              </div>
            </div>
            <div v-else class="text-slate-500">Envía una consulta para ver la respuesta y el contexto.</div>
          </div>
        </template>
      </Card>

      <Card class="shadow-sm">
        <template #title>
          <div class="flex items-center gap-2">
            <i class="pi pi-history text-primary-500"></i>
            <span>Historial de sesión</span>
          </div>
        </template>
        <template #content>
          <div v-if="history.length" class="space-y-4">
            <Panel v-for="item in history" :key="item.timestamp" toggleable collapsed>
              <template #header>
                <div class="flex flex-col gap-1">
                  <div class="flex items-center justify-between text-sm text-slate-600">
                    <span class="font-semibold">{{ item.client }}</span>
                    <span>{{ formatDate(item.timestamp) }}</span>
                  </div>
                  <span class="text-slate-800">{{ item.question }}</span>
                </div>
              </template>
              <template #default>
                <p class="mb-3 leading-relaxed text-slate-800">{{ item.answer }}</p>
                <div class="space-y-2">
                  <p class="text-sm font-semibold text-slate-700">Contexto</p>
                  <ul class="space-y-1 text-sm text-slate-600">
                    <li v-for="(chunk, idx) in item.chunks" :key="idx" class="rounded bg-slate-100 p-2">
                      <span class="font-semibold">{{ chunk.source }}</span> — página {{ chunk.page }}
                    </li>
                  </ul>
                </div>
              </template>
            </Panel>
          </div>
          <div v-else class="text-slate-500">Aún no hay preguntas en esta sesión.</div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import axios from 'axios'
import Dropdown from 'primevue/dropdown'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'
import Card from 'primevue/card'
import Divider from 'primevue/divider'
import ProgressSpinner from 'primevue/progressspinner'
import Tag from 'primevue/tag'
import Toast from 'primevue/toast'
import Panel from 'primevue/panel'
import { useToast } from 'primevue/usetoast'

const api = axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000' })
const toast = useToast()

const clients = ref([])
const selectedClient = ref(null)
const question = ref('')
const answer = ref('')
const chunks = ref([])
const loading = ref(false)
const history = ref([])

const canSubmit = computed(() => !!selectedClient.value && question.value.trim().length > 2)

const fetchClients = async () => {
  try {
    const { data } = await api.get('/clients')
    clients.value = data.map((client) => ({ label: client, value: client }))
  } catch (error) {
    clients.value = [
      { label: 'ACME', value: 'ACME' },
      { label: 'CAME', value: 'CAME' },
    ]
    toast.add({ severity: 'warn', summary: 'Clientes locales', detail: 'Usando clientes por defecto', life: 4000 })
  }
}

const submitQuery = async () => {
  if (!canSubmit.value) return
  loading.value = true
  answer.value = ''
  chunks.value = []
  try {
    const { data } = await api.post('/rag/query', {
      client: selectedClient.value,
      question: question.value,
    })
    answer.value = data.answer
    chunks.value = data.chunks
    history.value.unshift({
      client: selectedClient.value,
      question: question.value,
      answer: data.answer,
      chunks: data.chunks,
      timestamp: Date.now(),
    })
  } catch (error) {
    const message = error?.response?.data?.detail || 'No se pudo completar la consulta'
    toast.add({ severity: 'error', summary: 'Error', detail: message, life: 5000 })
  } finally {
    loading.value = false
  }
}

const clearAll = () => {
  answer.value = ''
  chunks.value = []
  history.value = []
  question.value = ''
}

const formatDate = (timestamp) => {
  return new Date(timestamp).toLocaleString()
}

onMounted(() => {
  fetchClients()
})
</script>

<style scoped>
.p-card { @apply shadow-md; }
</style>
