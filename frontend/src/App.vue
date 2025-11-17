<template>
  <div
    class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 p-6 text-slate-900 sm:p-10"
  >
    <Toast />
    <div class="mx-auto max-w-6xl">
      <header
        class="mb-8 flex flex-col gap-3 rounded-2xl bg-white/70 p-6 shadow-lg shadow-indigo-100 sm:flex-row sm:items-center sm:justify-between"
      >
        <div>
          <p class="text-xs uppercase tracking-[0.3em] text-indigo-500">
            Plataforma Inteligente
          </p>
          <h1 class="text-4xl font-semibold text-slate-900">RAG-COM</h1>
          <p class="text-base text-slate-600">
            Consulta procedimientos por cliente con contexto trazable.
          </p>
        </div>
        <div
          class="flex items-center gap-2 rounded-full bg-indigo-50 px-4 py-2 text-sm font-medium text-indigo-700"
        >
          <i class="pi pi-shield"></i>
          <span>Operaciones seguras y auditables</span>
        </div>
      </header>

      <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card class="modern-card lg:col-span-2">
          <template #title>
            <div class="flex items-center gap-2 text-indigo-700">
              <div
                class="flex h-10 w-10 items-center justify-center rounded-2xl bg-indigo-100 text-lg"
              >
                <i class="pi pi-comments"></i>
              </div>
              <div>
                <span class="text-sm uppercase tracking-wide text-indigo-400"
                  >Asistente</span
                >
                <p class="text-xl font-semibold text-slate-900">Consulta RAG</p>
              </div>
            </div>
          </template>
          <template #content>
            <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div class="flex flex-col gap-2">
                <label class="text-sm font-medium">Cliente</label>
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
                <label class="text-sm font-medium">Pregunta</label>
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
              <Button label="Limpiar" icon="pi pi-trash" @click="clearAll" />
            </div>

            <Divider class="my-6" />

            <div v-if="loading" class="flex items-center gap-3 text-slate-600">
              <ProgressSpinner
                style="width: 32px; height: 32px"
                strokeWidth="6"
              />
              <span>Generando respuesta...</span>
            </div>

            <div v-else>
              <div v-if="answer" class="space-y-4">
                <div>
                  <h2 class="mb-2 text-xl font-semibold">Respuesta</h2>
                  <p
                    class="rounded-2xl border border-white/60 bg-white/70 p-4 leading-relaxed shadow-sm shadow-indigo-50"
                  >
                    {{ answer }}
                  </p>
                </div>
                <div>
                  <h3 class="mb-2 text-lg font-semibold text-slate-800">
                    Fragmentos utilizados
                  </h3>
                  <div class="space-y-3">
                    <Card
                      v-for="(chunk, idx) in chunks"
                      :key="idx"
                      class="modern-subcard border border-transparent shadow-none"
                    >
                      <template #title>
                        <div
                          class="flex items-center gap-2 text-sm text-slate-500"
                        >
                          <Tag
                            :value="chunk.source"
                            class="uppercase tracking-wide"
                            severity="info"
                          />
                          <span class="text-indigo-500"
                            >Página: {{ chunk.page }}</span
                          >
                        </div>
                      </template>
                      <template #content>
                        <p
                          class="whitespace-pre-line leading-relaxed text-slate-800"
                        >
                          {{ chunk.text }}
                        </p>
                      </template>
                    </Card>
                  </div>
                </div>
              </div>
              <div v-else class="text-slate-500">
                Envía una consulta para ver la respuesta y el contexto.
              </div>
            </div>
          </template>
        </Card>

        <Card class="modern-card">
          <template #title>
            <div class="flex items-center gap-2 text-indigo-700">
              <div
                class="flex h-10 w-10 items-center justify-center rounded-2xl bg-indigo-100 text-lg"
              >
                <i class="pi pi-history"></i>
              </div>
              <div>
                <span class="text-sm uppercase tracking-wide text-indigo-400"
                  >Actividad</span
                >
                <p class="text-xl font-semibold text-slate-900">
                  Historial de sesión
                </p>
              </div>
            </div>
          </template>
          <template #content>
            <div v-if="history.length" class="space-y-4">
              <Panel
                v-for="item in history"
                :key="item.timestamp"
                toggleable
                collapsed
              >
                <template #header>
                  <div class="flex flex-col gap-1">
                    <div
                      class="flex items-center justify-between text-sm text-slate-600"
                    >
                      <span class="font-semibold">{{ item.client }}</span>
                      <span>{{ formatDate(item.timestamp) }}</span>
                    </div>
                    <span class="text-slate-800">{{ item.question }}</span>
                  </div>
                </template>
                <template #default>
                  <p class="mb-3 leading-relaxed text-slate-800">
                    {{ item.answer }}
                  </p>
                  <div class="space-y-2">
                    <p class="text-sm font-semibold text-slate-700">Contexto</p>
                    <ul class="space-y-1 text-sm text-slate-600">
                      <li
                        v-for="(chunk, idx) in item.chunks"
                        :key="idx"
                        class="rounded-lg bg-indigo-50/70 p-2 text-indigo-800"
                      >
                        <span class="font-semibold">{{ chunk.source }}</span> —
                        página {{ chunk.page }}
                      </li>
                    </ul>
                  </div>
                </template>
              </Panel>
            </div>
            <div v-else class="text-slate-500">
              Aún no hay preguntas en esta sesión.
            </div>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from "vue";
import axios from "axios";
import Dropdown from "primevue/dropdown";
import Textarea from "primevue/textarea";
import Button from "primevue/button";
import Card from "primevue/card";
import Divider from "primevue/divider";
import ProgressSpinner from "primevue/progressspinner";
import Tag from "primevue/tag";
import Toast from "primevue/toast";
import Panel from "primevue/panel";
import { useToast } from "primevue/usetoast";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
});
const toast = useToast();

const clients = ref([]);
const selectedClient = ref(null);
const question = ref("");
const answer = ref("");
const chunks = ref([]);
const loading = ref(false);
const history = ref([]);

const canSubmit = computed(
  () => !!selectedClient.value && question.value.trim().length > 2
);

const fetchClients = async () => {
  try {
    const { data } = await api.get("/clients");
    clients.value = data.map((client) => ({ label: client, value: client }));
  } catch (error) {
    clients.value = [
      { label: "ACME", value: "ACME" },
      { label: "CAME", value: "CAME" },
    ];
    toast.add({
      severity: "warn",
      summary: "Clientes locales",
      detail: "Usando clientes por defecto",
      life: 4000,
    });
  }
};

const submitQuery = async () => {
  if (!canSubmit.value) return;
  loading.value = true;
  answer.value = "";
  chunks.value = [];
  try {
    const { data } = await api.post("/rag/query", {
      client: selectedClient.value,
      question: question.value,
    });
    answer.value = data.answer;
    chunks.value = data.chunks;
    history.value.unshift({
      client: selectedClient.value,
      question: question.value,
      answer: data.answer,
      chunks: data.chunks,
      timestamp: Date.now(),
    });
  } catch (error) {
    const message =
      error?.response?.data?.detail || "No se pudo completar la consulta";
    toast.add({
      severity: "error",
      summary: "Error",
      detail: message,
      life: 5000,
    });
  } finally {
    loading.value = false;
  }
};

const clearAll = () => {
  answer.value = "";
  chunks.value = [];
  history.value = [];
  question.value = "";
};

const formatDate = (timestamp) => {
  return new Date(timestamp).toLocaleString();
};

onMounted(() => {
  fetchClients();
});
</script>

<style scoped>
.modern-card {
  background: linear-gradient(
    145deg,
    rgba(255, 255, 255, 0.95),
    rgba(237, 244, 255, 0.9)
  );
  border-radius: 1.5rem;
  border: 1px solid rgba(202, 206, 211, 0.25);
  box-shadow: 0 20px 45px rgba(143, 166, 221, 0.08);
  backdrop-filter: blur(10px);
}

.modern-subcard {
  background: linear-gradient(
    135deg,
    rgba(250, 250, 255, 0.95),
    rgba(224, 231, 255, 0.9)
  );
  border-radius: 1rem;
  border: 1px solid rgba(215, 215, 228, 0.1);
  box-shadow: 0 12px 30px rgba(99, 102, 241, 0.12);
}

:deep(.p-panel) {
  border: none;
  background: rgba(255, 255, 255, 0.85);
  border-radius: 1rem;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
}

:deep(.p-panel-header) {
  padding: 1rem 1.25rem;
  background: transparent;
}

:deep(.p-panel-content) {
  background: transparent;
}

:deep(.p-dropdown),
:deep(.p-inputtextarea) {
  border-radius: 1rem;
  border: 1px solid rgba(149, 150, 207, 0.2);
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 5px 20px rgba(15, 23, 42, 0.05);
  color: #0f172a;
}

:deep(.p-dropdown.p-focus),
:deep(.p-inputtextarea:focus) {
  border-color: rgba(37, 99, 235, 0.5);
  box-shadow: 0 0 0 1px rgba(69, 105, 182, 0.15);
}

:deep(.p-button) {
  border-radius: 999px;
  background: linear-gradient(120deg, #4f46e5, #7c3aed);
  border: none;
  box-shadow: 0 10px 25px rgba(79, 70, 229, 0.35);
}

:deep(.p-button .p-button-label) {
  font-weight: 600;
  letter-spacing: 0.02em;
}

:deep(.p-button:enabled:hover) {
  background: linear-gradient(120deg, #4338ca, #6d28d9);
}

:deep(.p-button.p-button-outlined) {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(79, 70, 229, 0.25);
  color: #4f46e5;
  box-shadow: 0 10px 25px rgba(79, 70, 229, 0.12);
}

:deep(.p-button.p-button-outlined:enabled:hover) {
  background: rgba(99, 102, 241, 0.1);
  border-color: rgba(79, 70, 229, 0.5);
}
</style>
