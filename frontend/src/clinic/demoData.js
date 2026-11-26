export const demoDate = '2026-11-19'
export const demoCredentials = { email: 'ana@clinica.example', password: 'ClinicaA3!' }
export const demoVeterinarian = { id: 1, nome_completo: 'Dra. Ana Lima', situacao: 'ativo' }

const marina = { id: 1, nome_completo: 'Marina Alves' }
const rafael = { id: 2, nome_completo: 'Rafael Costa' }
const beatriz = { id: 3, nome_completo: 'Beatriz Souza' }
const dog = { id: 1, nome: 'Canina' }
const cat = { id: 2, nome: 'Felina' }
const luna = { id: 1, nome: 'Luna' }
const thor = { id: 2, nome: 'Thor' }
const mia = { id: 3, nome: 'Mia' }
const address = { id: 1, cep: '01001000', logradouro: 'Praça da Sé', numero: '128', complemento: '', bairro: 'Sé', cidade: 'São Paulo', uf: 'SP', ibge: '3550308' }

export const demoAddresses = {
  '01001000': address,
  '20040002': { cep: '20040002', logradouro: 'Rua da Assembleia', bairro: 'Centro', cidade: 'Rio de Janeiro', uf: 'RJ', ibge: '3304557' },
}

export const seed = {
  tutors: [
    { ...marina, cpf: '52998224725', telefone: '11987654321', email: 'marina@example.com', data_nascimento: '1990-05-20', endereco: address, endereco_id: 1, situacao: 'ativo' },
    { ...rafael, cpf: '11144477735', telefone: '21976543210', email: 'rafael@example.com', data_nascimento: '1988-04-19', endereco: { ...address, id: 2, numero: '80' }, endereco_id: 2, situacao: 'ativo' },
    { ...beatriz, cpf: '12345678909', telefone: '31998765432', email: 'beatriz@example.com', data_nascimento: '1994-06-24', endereco: { ...address, id: 3, numero: '216' }, endereco_id: 3, situacao: 'inativo' },
  ],
  animals: [
    { ...luna, tutor: marina, especie: dog, raca: null, sexo: 'F', data_nascimento: '2022-05-10', peso_atual: 16.8, cor: 'Caramelo', situacao: 'ativo', portrait: 'luna', chips: [{ codigo: '900000000000124', data_vinculo: '2026-11-18', veterinario: demoVeterinarian.nome_completo, atual: true }] },
    { ...thor, tutor: rafael, especie: dog, raca: null, sexo: 'M', data_nascimento: '2021-04-05', peso_atual: 23.4, cor: 'Preto e caramelo', situacao: 'ativo', portrait: 'thor', chips: [{ codigo: '900000000000987', data_vinculo: '2026-11-19', veterinario: demoVeterinarian.nome_completo, atual: true }] },
    { ...mia, tutor: beatriz, especie: cat, raca: null, sexo: 'F', data_nascimento: '2023-03-19', peso_atual: 4.2, cor: 'Cinza', situacao: 'ativo', portrait: 'mia', chips: [] },
  ],
  vets: [demoVeterinarian],
  species: [dog, cat, { id: 3, nome: 'Ave' }],
  breeds: [{ id: 1, nome: 'Labrador', especie_id: 1 }, { id: 2, nome: 'Siamês', especie_id: 2 }],
  appointments: [
    { id: 1, animal: luna, veterinario: demoVeterinarian, data_hora: '2026-11-19T09:00:00', motivo: 'Consulta de rotina', situacao: 'realizada', peso: 16.8, observacoes: 'Exame de rotina registrado.' },
    { id: 2, animal: thor, veterinario: demoVeterinarian, data_hora: '2026-11-19T10:30:00', motivo: 'Retorno', situacao: 'agendada' },
    { id: 3, animal: mia, veterinario: demoVeterinarian, data_hora: '2026-11-19T14:00:00', motivo: 'Avaliação clínica', situacao: 'agendada' },
  ],
  vaccines: [
    { id: 1, animal: luna, veterinario: demoVeterinarian, nome_vacina: 'Antirrábica', tipo_vacina: 'Antirrábica', antirrabica: true, data_aplicacao: '2026-11-19', data_proxima_dose: '2027-11-19', situacao: 'aplicada', fabricante: 'Laboratório Exemplo', numero_lote: 'AR26-08', dose: 'Dose única', validade_lote: '2027-10-01' },
    { id: 2, animal: luna, veterinario: demoVeterinarian, nome_vacina: 'Polivalente', tipo_vacina: 'Polivalente', antirrabica: false, data_aplicacao: '2026-11-18', data_proxima_dose: '2027-11-18', situacao: 'aplicada', fabricante: 'Laboratório Exemplo', numero_lote: 'PV26-09', dose: 'Reforço', validade_lote: '2027-08-01' },
    { id: 3, animal: thor, veterinario: demoVeterinarian, nome_vacina: 'Polivalente', tipo_vacina: 'Polivalente', antirrabica: false, data_aplicacao: null, data_proxima_dose: '2026-11-20', situacao: 'agendada', fabricante: 'Laboratório Exemplo', numero_lote: 'PV26-09', dose: 'Reforço', validade_lote: '2027-08-01' },
  ],
  integrations: [
    { id: 1, animal: luna, vacina_id: 1, tipo: 'Vacina antirrábica', situacao: 'pendente', data: '2026-11-19', tentativas: 1, erro: 'Serviço temporariamente indisponível.', protocolo: null },
    { id: 2, animal: thor, vacina_id: null, tipo: 'Cadastro de animal', situacao: 'pendente', data: '2026-11-19', tentativas: 0, erro: null, protocolo: null },
  ],
}
