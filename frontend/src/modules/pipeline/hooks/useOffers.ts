import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { App } from "antd";
import { offerService, type OfferFilters } from "../services/offerService";
import type { OfferCreate, OfferUpdate } from "../../../types/pipeline";

export function useOffers(filters: OfferFilters = {}) {
  return useQuery({
    queryKey: ["offers", filters],
    queryFn: () => offerService.list(filters),
  });
}

export function useOffer(id: string | undefined) {
  return useQuery({
    queryKey: ["offers", id],
    queryFn: () => offerService.get(id!),
    enabled: !!id,
  });
}

export function useOfferTimeline(id: string | undefined) {
  return useQuery({
    queryKey: ["offers", id, "timeline"],
    queryFn: () => offerService.getTimeline(id!),
    enabled: !!id,
  });
}

export function useCreateOffer() {
  const queryClient = useQueryClient();
  const { message } = App.useApp();

  return useMutation({
    mutationFn: (payload: OfferCreate) => offerService.create(payload),
    onSuccess: () => {
      message.success("Ofertă creată cu succes.");
      queryClient.invalidateQueries({ queryKey: ["offers"] });
    },
    onError: () => message.error("Eroare la crearea ofertei."),
  });
}

export function useUpdateOffer() {
  const queryClient = useQueryClient();
  const { message } = App.useApp();

  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: OfferUpdate }) =>
      offerService.update(id, payload),
    onSuccess: () => {
      message.success("Ofertă actualizată.");
      queryClient.invalidateQueries({ queryKey: ["offers"] });
    },
    onError: () => message.error("Eroare la actualizare."),
  });
}

export function useDeleteOffer() {
  const queryClient = useQueryClient();
  const { message } = App.useApp();

  return useMutation({
    mutationFn: offerService.delete,
    onSuccess: () => {
      message.success("Ofertă ștearsă.");
      queryClient.invalidateQueries({ queryKey: ["offers"] });
    },
    onError: () => message.error("Eroare la ștergere."),
  });
}

export function useSubmitOffer() {
  const queryClient = useQueryClient();
  const { message } = App.useApp();

  return useMutation({
    mutationFn: (id: string) => offerService.submit(id),
    onSuccess: () => {
      message.success("Ofertă trimisă pentru aprobare.");
      queryClient.invalidateQueries({ queryKey: ["offers"] });
    },
    onError: () => message.error("Eroare la trimitere."),
  });
}

export function useCreateOfferVersion() {
  const queryClient = useQueryClient();
  const { message } = App.useApp();

  return useMutation({
    mutationFn: (id: string) => offerService.createVersion(id),
    onSuccess: () => {
      message.success("Versiune nouă creată.");
      queryClient.invalidateQueries({ queryKey: ["offers"] });
    },
    onError: () => message.error("Eroare la creare versiune."),
  });
}

export function useSendOffer() {
  const queryClient = useQueryClient();
  const { message } = App.useApp();

  return useMutation({
    mutationFn: (id: string) => offerService.send(id),
    onSuccess: () => {
      message.success("Ofertă trimisă clientului.");
      queryClient.invalidateQueries({ queryKey: ["offers"] });
    },
    onError: () => message.error("Eroare la trimitere."),
  });
}

export function useConvertToContract() {
  const queryClient = useQueryClient();
  const { message } = App.useApp();

  return useMutation({
    mutationFn: (id: string) => offerService.convertToContract(id),
    onSuccess: () => {
      message.success("Contract creat din ofertă.");
      queryClient.invalidateQueries({ queryKey: ["offers"] });
      queryClient.invalidateQueries({ queryKey: ["contracts"] });
    },
    onError: () => message.error("Eroare la conversie."),
  });
}

export function useSearchProducts(search?: string, category?: string) {
  return useQuery({
    queryKey: ["products", search, category],
    queryFn: () => offerService.searchProducts(search, category),
    enabled: search !== undefined,
  });
}
